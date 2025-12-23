"""
Audio Processor Task
Celery task for processing audio with the professional AudioPipeline
"""

from celery_app import celery_app
from typing import List
import os
import tempfile
from datetime import datetime
import json
import numpy as np

from audio_engine.pipeline import AudioPipeline
from storage.b2_client import B2Client
from config import settings


def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj



@celery_app.task(bind=True)
def process_audio_job(self, job_id: str, stem_urls: List[str], genre_override: str = None):
    """
    Professional audio processing pipeline with genre-aware processing
    
    Pipeline stages:
    1. Download stems from B2
    2. Process through AudioPipeline (Genre Detection → Mix → Master)
    3. Upload results to B2
    4. Generate report
    
    Args:
        job_id: Unique job identifier
        stem_urls: List of B2 file paths for stems
        genre_override: Optional genre to use instead of auto-detection
    """
    try:
        # Update job status
        self.update_state(state='PROGRESS', meta={'progress': 0, 'stage': 'initializing'})
        
        # Initialize components
        b2_client = B2Client()
        pipeline = AudioPipeline(sample_rate=settings.SAMPLE_RATE)
        
        # Create temp directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Stage 1: Download stems (0-15%)
            self.update_state(state='PROGRESS', meta={'progress': 0, 'stage': 'downloading'})
            
            stem_files = []
            for i, url in enumerate(stem_urls):
                file_name = url.split('/')[-1]
                file_path = os.path.join(temp_dir, file_name)
                
                # Download from B2
                content = b2_client.download_file(
                    f"{job_id}/{file_name}",
                    bucket_name=settings.B2_BUCKET_INPUT
                )
                
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                stem_files.append(file_path)
                
                progress = int((i + 1) / len(stem_urls) * 15)
                self.update_state(state='PROGRESS', meta={
                    'progress': progress, 
                    'stage': 'downloading',
                    'detail': f'Downloaded {i+1}/{len(stem_urls)} stems'
                })
            
            # Stage 2: Process through AudioPipeline (15-90%)
            # The pipeline handles: Genre Detection → Mixing → Mastering
            
            mix_output = os.path.join(temp_dir, 'mix.wav')
            master_output = os.path.join(temp_dir, 'master.wav')
            
            def progress_callback(progress, stage):
                """Callback for pipeline progress updates"""
                # Map pipeline progress (0-100) to our range (15-90)
                celery_progress = 15 + int(progress * 0.75)
                self.update_state(state='PROGRESS', meta={
                    'progress': celery_progress,
                    'stage': stage,
                    'detail': f'{stage}...'
                })
            
            # Process audio with genre-aware pipeline
            self.update_state(state='PROGRESS', meta={
                'progress': 15, 
                'stage': 'processing',
                'detail': 'Starting genre-aware audio engine...'
            })
            
            report = pipeline.process(
                stem_files=stem_files,
                output_mix_path=mix_output,
                output_master_path=master_output,
                target_lufs=settings.LUFS_POP,  # Will be overridden by genre
                ceiling_dbTP=settings.TRUE_PEAK_CEILING_DBTP,
                max_width_percent=settings.MAX_STEREO_WIDTH_PCT,
                preset='balanced',
                genre_override=genre_override,  # Pass genre override!
                progress_callback=progress_callback
            )
            
            # Stage 3: Upload to B2 (90-95%)
            self.update_state(state='PROGRESS', meta={
                'progress': 90, 
                'stage': 'uploading',
                'detail': 'Uploading mix...'
            })
            
            # Upload mix WAV
            with open(mix_output, 'rb') as f:
                mix_content = f.read()
            
            mix_path = b2_client.upload_file(
                mix_content,
                f"{job_id}/mix.wav",
                bucket_name=settings.B2_BUCKET_OUTPUT
            )
            
            # Upload master WAV
            with open(master_output, 'rb') as f:
                master_content = f.read()
            
            master_path = b2_client.upload_file(
                master_content,
                f"{job_id}/master.wav",
                bucket_name=settings.B2_BUCKET_OUTPUT
            )
            
            self.update_state(state='PROGRESS', meta={
                'progress': 92, 
                'stage': 'uploading',
                'detail': 'Creating MP3...'
            })
            
            # Create MP3 version of master
            mp3_file = os.path.join(temp_dir, 'master.mp3')
            os.system(f'ffmpeg -i {master_output} -codec:a libmp3lame -qscale:a 0 {mp3_file} -y 2>&1')
            
            with open(mp3_file, 'rb') as f:
                mp3_content = f.read()
            
            mp3_path = b2_client.upload_file(
                mp3_content,
                f"{job_id}/master.mp3",
                bucket_name=settings.B2_BUCKET_OUTPUT
            )
            
            self.update_state(state='PROGRESS', meta={
                'progress': 94, 
                'stage': 'uploading',
                'detail': 'Uploading report...'
            })
            
            # Custom JSON encoder for numpy types
            import numpy as np
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, np.bool_):
                        return bool(obj)
                    if isinstance(obj, np.integer):
                        return int(obj)
                    if isinstance(obj, np.floating):
                        return float(obj)
                    if isinstance(obj, np.ndarray):
                        return obj.tolist()
                    return super().default(obj)
            
            # Upload report as JSON
            report_json = json.dumps(report, indent=2, cls=NumpyEncoder)
            b2_client.upload_file(
                report_json.encode('utf-8'),
                f"{job_id}/report.json",
                bucket_name=settings.B2_BUCKET_OUTPUT
            )
            
            # Stage 4: Generate signed URLs (95-100%)
            self.update_state(state='PROGRESS', meta={
                'progress': 95, 
                'stage': 'finalizing',
                'detail': 'Generating download URLs...'
            })
            
            # Generate signed download URLs (24 hour expiry)
            mix_url = b2_client.get_download_url(
                mix_path,
                bucket_name=settings.B2_BUCKET_OUTPUT,
                expiry_seconds=86400
            )
            
            master_url = b2_client.get_download_url(
                master_path,
                bucket_name=settings.B2_BUCKET_OUTPUT,
                expiry_seconds=86400
            )
            
            mp3_url = b2_client.get_download_url(
                mp3_path,
                bucket_name=settings.B2_BUCKET_OUTPUT,
                expiry_seconds=86400
            )
            
            self.update_state(state='PROGRESS', meta={'progress': 100, 'stage': 'complete'})
            
            # Return comprehensive result (convert numpy types for JSON serialization)
            return convert_numpy_types({
                'status': 'complete',
                'job_id': job_id,
                'completed_at': datetime.utcnow().isoformat(),
                'urls': {
                    'mix_wav': mix_url,
                    'master_wav': master_url,
                    'master_mp3': mp3_url
                },
                # Legacy compatibility
                'download_url': master_url,
                'mp3_url': mp3_url,
                # Processing report summary
                'report_summary': {
                    'processing_time': report.get('timing', {}).get('total_seconds', 0),
                    'stem_count': len(stem_urls),
                    'final_lufs': report.get('master_report', {}).get('final_metrics', {}).get('lufs', -14),
                    'true_peak_dbTP': report.get('master_report', {}).get('final_metrics', {}).get('true_peak_dbTP', -1),
                    'mono_compatible': report.get('master_report', {}).get('mono_compatibility', {}).get('mono_compatible', True),
                    'qc_passed': report.get('master_report', {}).get('qc_results', {}).get('all_safe', True),
                    'genre': report.get('genre', {}).get('name', 'Unknown'),
                    'genre_confidence': report.get('genre', {}).get('confidence', 0)
                }
            })
            
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # Log error
        print(f"ERROR in audio processing job {job_id}:")
        print(error_trace)
        
        # Update state with error info
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'error_type': type(e).__name__,
                'traceback': error_trace
            }
        )
        
        # Return error dict instead of raising to avoid serialization issues
        return {
            'status': 'failed',
            'error': error_msg,
            'error_type': type(e).__name__,
            'job_id': job_id,
            'failed_at': datetime.utcnow().isoformat()
        }
