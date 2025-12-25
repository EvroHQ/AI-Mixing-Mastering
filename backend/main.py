from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
import uuid
import os
from datetime import datetime
import io

from tasks.audio_processor import process_audio_job
from storage.b2_client import B2Client
from config import settings

app = FastAPI(
    title="MixMaster API",
    description="AI-powered audio mixing and mastering API",
    version="1.0.0"
)

# CORS middleware - use ALLOWED_ORIGINS from settings
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize B2 client
b2_client = B2Client()

# In-memory job storage (replace with Redis in production)
jobs = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/upload")
async def upload_stems(
    files: List[UploadFile] = File(...),
    genre: str = None
):
    """
    Upload audio stems for processing
    
    Args:
        files: List of audio files (WAV, AIFF, FLAC, MP3)
        genre: Optional genre override (if None, auto-detect)
        
    Returns:
        job_id: Unique identifier for tracking the job
    """
    try:
        # Validate files
        if len(files) > 32:
            raise HTTPException(status_code=400, detail="Maximum 32 files allowed")
        
        # Validate genre if provided
        if genre:
            from audio_engine import GenrePresets
            valid_genres = GenrePresets.list_genres()
            if genre not in valid_genres:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid genre. Valid options: {valid_genres}"
                )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Upload files to B2
        stem_urls = []
        for file in files:
            if not file.filename.endswith(('.wav', '.aiff', '.flac', '.mp3')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}"
                )
            
            file_content = await file.read()
            b2_url = b2_client.upload_file(
                file_content,
                f"{job_id}/{file.filename}",
                bucket_name="mixmaster-input"
            )
            stem_urls.append(b2_url)
        
        # Queue processing task with optional genre
        task = process_audio_job.delay(job_id, stem_urls, genre_override=genre)
        
        # Create job record
        jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "stem_count": len(files),
            "task_id": task.id,
            "genre_override": genre
        }
        
        return JSONResponse({
            "job_id": job_id,
            "status": "queued",
            "message": f"Processing {len(files)} stems",
            "genre_mode": "manual" if genre else "auto-detect"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get processing status for a job
    
    Args:
        job_id: Job identifier
        
    Returns:
        status: Current job status
        progress: Processing progress (0-100)
        download_url: URL to download final master (if complete)
    """
    from celery.result import AsyncResult
    from celery_app import celery_app
    
    # Check if job exists in our records
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    task_id = job.get("task_id")
    
    # Query Celery for task status if we have a task_id
    if task_id:
        try:
            result = AsyncResult(task_id, app=celery_app)
            
            if result.state == 'PENDING':
                status = 'queued'
                progress = 0
                stage = 'initializing'
                detail = ''
            elif result.state == 'PROGRESS':
                status = 'processing'
                progress = result.info.get('progress', 0) if result.info else 0
                stage = result.info.get('stage', 'processing') if result.info else 'processing'
                detail = result.info.get('detail', '') if result.info else ''
            elif result.state == 'SUCCESS':
                status = 'complete'
                progress = 100
                stage = 'complete'
                detail = 'Processing complete!'
                # Get result data and update job
                result_data = result.result
                if result_data and isinstance(result_data, dict):
                    job.update(result_data)
            elif result.state == 'FAILURE':
                status = 'failed'
                progress = 0
                stage = 'error'
                detail = ''
                if result.info:
                    job['error'] = str(result.info)
            else:
                # Fallback to stored status
                status = job.get("status", "queued")
                progress = job.get("progress", 0)
                stage = job.get("stage", "processing")
                detail = job.get("detail", "")
        except Exception as e:
            # If Celery query fails, use stored status
            print(f"Error querying Celery task {task_id}: {e}")
            status = job.get("status", "queued")
            progress = job.get("progress", 0)
            stage = job.get("stage", "processing")
            detail = job.get("detail", "")
    else:
        # No task_id, use stored status
        status = job.get("status", "queued")
        progress = job.get("progress", 0)
        stage = job.get("stage", "initializing")
        detail = job.get("detail", "")
    
    response = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "created_at": job["created_at"],
        "stage": stage,
        "detail": detail,
    }
    
    if status == "complete" or job.get("status") == "complete":
        response["download_url"] = job.get("download_url")
        response["mp3_url"] = job.get("mp3_url")
        response["completed_at"] = job.get("completed_at")
    
    if status == "failed" or job.get("status") == "error":
        response["error"] = job.get("error", "Processing failed")
    
    return JSONResponse(response)


@app.get("/api/download/{job_id}")
async def get_download_url(job_id: str):
    """
    Get signed download URL for completed job
    
    Args:
        job_id: Job identifier
        
    Returns:
        download_url: Signed URL for downloading the master
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "complete":
        raise HTTPException(status_code=400, detail="Job not complete")
    
    # Generate signed URL (24-hour expiry)
    download_url = b2_client.get_download_url(
        f"{job_id}/master.wav",
        bucket_name="mixmaster-output"
    )
    
    return JSONResponse({"download_url": download_url})


@app.get("/api/audio/{job_id}/{file_type}")
async def proxy_audio(job_id: str, file_type: str):
    """
    Proxy audio files from B2 with proper CORS headers
    
    Args:
        job_id: Job identifier
        file_type: 'wav' or 'mp3'
    """
    if file_type not in ['wav', 'mp3']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_name = f"{job_id}/master.{file_type}"
    
    try:
        # Download file from B2
        file_content = b2_client.download_file(
            file_name,
            bucket_name="mixmaster-output"
        )
        
        # Return as streaming response with proper headers
        media_type = "audio/wav" if file_type == "wav" else "audio/mpeg"
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=media_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(file_content)),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")


@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """
    Manually delete job and associated files
    
    Args:
        job_id: Job identifier
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files from B2
    b2_client.delete_folder(f"{job_id}/", bucket_name="mixmaster-input")
    b2_client.delete_folder(f"{job_id}/", bucket_name="mixmaster-output")
    
    # Remove from jobs dict
    del jobs[job_id]
    
    return JSONResponse({"message": "Job deleted successfully"})


@app.get("/api/genres")
async def get_available_genres():
    """
    Get list of available music genres with descriptions
    
    Returns:
        List of genres with id, name, description, and target LUFS
    """
    from audio_engine import AudioPipeline
    
    genres = AudioPipeline.get_available_genres()
    
    return JSONResponse({
        "genres": genres,
        "count": len(genres)
    })


@app.post("/api/analyze-genre")
async def analyze_genre(files: List[UploadFile] = File(...)):
    """
    Quick genre detection from uploaded stems (before full processing)
    
    Args:
        files: List of audio files to analyze
        
    Returns:
        Detected genre with confidence score and recommended settings
    """
    import tempfile
    import shutil
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting genre analysis with {len(files)} files")
    
    try:
        # Create temp directory for files
        temp_dir = tempfile.mkdtemp()
        temp_files = []
        
        for file in files:
            # Validate file type
            if not file.filename.endswith(('.wav', '.aiff', '.flac', '.mp3')):
                logger.warning(f"Skipping invalid file: {file.filename}")
                continue
            
            logger.info(f"Processing file: {file.filename}")
            
            # Save to temp file using streaming to avoid memory issues
            temp_path = os.path.join(temp_dir, file.filename)
            with open(temp_path, 'wb') as f:
                # Stream in chunks to avoid loading entire file in memory
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    f.write(chunk)
            temp_files.append(temp_path)
            logger.info(f"Saved temp file: {temp_path}")
        
        if not temp_files:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail="No valid audio files")
        
        logger.info(f"Analyzing {len(temp_files)} files for genre")
        
        # Analyze genre
        from audio_engine import AudioPipeline
        pipeline = AudioPipeline()
        result = pipeline.analyze_genre_only(temp_files)
        
        logger.info(f"Genre detected: {result.get('genre_name', 'unknown')}")
        
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return JSONResponse({
            "genre": result['genre'],
            "genre_name": result['genre_name'],
            "confidence": result['confidence'],
            "description": result['description'],
            "all_scores": result['all_scores'],
            "recommended_settings": result['recommended_settings'],
            "available_genres": result['available_genres'],
            "analysis": result.get('analysis', {})  # For debugging
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Genre analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# Alias for backward compatibility
@app.post("/api/upload-with-genre")
async def upload_stems_with_genre_alias(
    files: List[UploadFile] = File(...),
    genre: str = None
):
    """Alias for /api/upload with genre parameter"""
    return await upload_stems(files, genre)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

