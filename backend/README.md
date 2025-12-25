# Backend API

Python FastAPI backend for audio processing.

## Endpoints

- `POST /api/upload` - Upload stems and start processing
- `POST /api/analyze-genre` - Detect genre from stems
- `GET /api/status/{job_id}` - Check job status
- `GET /api/download/{job_id}` - Get download URL
- `GET /api/genres` - List available genres

## Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start API
uvicorn main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A celery_app worker --loglevel=info
```

## Environment Variables

```
REDIS_URL=redis://localhost:6379
B2_APPLICATION_KEY_ID=your_key
B2_APPLICATION_KEY=your_secret
ALLOWED_ORIGINS=http://localhost:3000
```
