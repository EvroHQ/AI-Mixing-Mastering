# MixMaster Pro - Development Setup (No Docker)

## Quick Start for Audio Engine Development

This setup allows you to develop and test the mixing/mastering algorithms without Docker infrastructure.

### Prerequisites

- Python 3.10+
- FFmpeg (for audio conversion)
- Backblaze B2 account
- 8GB+ RAM
- GPU optional (CPU fallback available)

### Installation

```bash
# 1. Create virtual environment
cd c:/Users/EvroHQ/Desktop/mixmasterbis/backend
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp ../.env.example ../.env
# Edit .env with your B2 credentials

# 4. Run development server
python -m api.main
```

### Development Workflow

```bash
# Terminal 1: API Server
cd backend
venv\Scripts\activate
python -m uvicorn api.main:app --reload

# Terminal 2: Test audio processing
cd backend
venv\Scripts\activate
python scripts/test_audio_engine.py
```

### Architecture (Development Mode)

```
Frontend (Next.js) → FastAPI → Audio Engine → Backblaze B2
                                    ↓
                              SQLite (local)
```

**Simplified from production**:

- ✅ Full audio engine (analyzer, mixer, masterer)
- ✅ Backblaze B2 storage
- ✅ FastAPI REST API
- ✅ SQLite database (instead of PostgreSQL)
- ✅ Synchronous processing (instead of Celery)
- ❌ No Redis/Celery (direct execution)
- ❌ No Docker containers
- ❌ No Nginx (direct FastAPI)
- ❌ No monitoring (Prometheus/Grafana)

### Testing Audio Processing

```python
# scripts/test_audio_engine.py
from audio_engine.pipeline import AudioPipeline

# Process stems
pipeline = AudioPipeline()
result = pipeline.process(
    stems=['kick.wav', 'bass.wav', 'vocals.wav'],
    preset='Electro House',
    targets={'lufs': -10}
)

print(f"Mix: {result['mix_url']}")
print(f"Master: {result['master_url']}")
print(f"LUFS: {result['metrics']['lufs']}")
```

### File Structure (Development)

```
backend/
├── venv/                    # Virtual environment
├── api/
│   └── main.py             # FastAPI app (simplified)
├── audio_engine/
│   ├── analyzer/           # Audio analysis
│   ├── mixer/              # Mixing engine
│   ├── masterer/           # Mastering engine
│   └── pipeline.py         # Main pipeline
├── storage/
│   └── b2_client.py        # B2 storage
├── database/
│   └── sqlite_db.py        # SQLite database
├── scripts/
│   ├── test_audio_engine.py
│   └── benchmark.py
└── requirements.txt
```

### Next Steps

1. ✅ Install dependencies
2. ✅ Configure B2 credentials
3. ✅ Test audio analysis
4. ✅ Test mixing algorithms
5. ✅ Test mastering chain
6. ✅ Validate audio quality
7. 🔄 Iterate on presets

### Migration to Production

When ready for production:

1. Add Celery for async processing
2. Switch SQLite → PostgreSQL
3. Add Redis for job queue
4. Containerize with Docker
5. Add monitoring
6. Deploy to cloud

---

**Focus**: Audio quality first, infrastructure later! 🎵
