"""
Mock Backend API for MixMaster
Simple FastAPI server that simulates audio processing without Redis/Celery/B2
Perfect for testing the frontend UI
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import uuid
import time
import asyncio
from datetime import datetime
import os

app = FastAPI(title="MixMaster Mock API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
jobs = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/upload")
async def upload_stems(files: List[UploadFile] = File(...)):
    """Mock upload endpoint - simulates file upload"""
    try:
        if len(files) > 12:
            raise HTTPException(status_code=400, detail="Maximum 12 files allowed")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job record
        jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "stem_count": len(files),
            "start_time": time.time()
        }
        
        # Start background task to simulate processing
        asyncio.create_task(simulate_processing(job_id))
        
        return JSONResponse({
            "job_id": job_id,
            "status": "processing",
            "message": f"Processing {len(files)} stems"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def simulate_processing(job_id: str):
    """Simulate audio processing with progress updates"""
    # Simulate processing stages
    stages = [
        (10, 2),   # Upload: 10% in 2 seconds
        (30, 3),   # Analyze: 30% in 3 seconds  
        (70, 5),   # Mix: 70% in 5 seconds
        (90, 2),   # Master: 90% in 2 seconds
        (100, 1),  # Complete: 100% in 1 second
    ]
    
    for target_progress, duration in stages:
        await asyncio.sleep(duration)
        if job_id in jobs:
            jobs[job_id]["progress"] = target_progress
    
    # Mark as complete
    if job_id in jobs:
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["download_url"] = f"http://localhost:8000/api/download/{job_id}/master.wav"
        jobs[job_id]["original_url"] = f"http://localhost:8000/api/download/{job_id}/original.wav"
        jobs[job_id]["mp3_url"] = f"http://localhost:8000/api/download/{job_id}/master.mp3"

@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Get processing status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    response = {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress", 0),
        "created_at": job["created_at"],
    }
    
    if job["status"] == "complete":
        response["download_url"] = job.get("download_url")
        response["original_url"] = job.get("original_url")
        response["mp3_url"] = job.get("mp3_url")
    
    return JSONResponse(response)

@app.get("/api/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """Mock download endpoint - returns a placeholder message"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JSONResponse({
        "message": "This is a mock API. In production, this would return the actual audio file.",
        "job_id": job_id,
        "filename": filename,
        "note": "The real backend would stream the WAV/MP3 file here."
    })

@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Delete job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del jobs[job_id]
    return JSONResponse({"message": "Job deleted successfully"})

if __name__ == "__main__":
    import uvicorn
    print("🎵 MixMaster Mock API Starting...")
    print("📍 Running on: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("✨ This is a MOCK server for testing the UI")
    print("⚡ Processing is simulated (takes ~13 seconds)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
