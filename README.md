# 🎵 MixMaster Pro

**Professional AI-Powered Audio Mixing & Mastering Pipeline**

Transform up to 12 audio stems into studio-grade mixes and masters in under 2 minutes.

## ✨ Features

- **Multi-Stem Processing**: Handle up to 12 stems (24-bit WAV/AIFF, 44.1/48 kHz)
- **AI-Assisted Mixing**: Neural policy model predicts optimal mixing parameters
- **Professional DSP**: High-quality audio processing using Spotify's Pedalboard
- **Intelligent Mastering**: Reference matching, multi-band compression, true-peak limiting
- **Safety Guardrails**: Automatic quality checks and constraints
- **Fast Processing**: ≤120 seconds for 4-minute tracks
- **Multiple Presets**: Electro House, Pop, Hip-Hop, Rock, and more
- **Detailed Reports**: Comprehensive JSON reports with metrics and QC results

## 🎯 Quality Targets

- **Loudness**: −14 LUFS (streaming), −10 LUFS (pop), −8 LUFS (club)
- **True Peak**: ≤ −1 dBTP
- **Stereo Width**: ≤ 140%
- **Mono Correlation**: ≥ 0.1
- **Crest Factor**: Preserved (no over-compression)

## 🏗️ Architecture

```
Frontend (Next.js) → Nginx → FastAPI → Celery Workers (GPU) → MinIO/PostgreSQL
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with CUDA support (for GPU workers)
- 16GB+ RAM recommended
- 50GB+ free disk space

### 1. Clone & Setup

```bash
git clone <repository-url>
cd mixmasterbis

# Copy environment file
cp .env.example .env

# Edit .env with your passwords
nano .env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Applications

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower (Celery Monitor)**: http://localhost:5555
- **Grafana (Metrics)**: http://localhost:3001
- **MinIO Console**: http://localhost:9001

### 4. Upload & Process

1. Navigate to http://localhost:3000
2. Upload up to 12 audio stems
3. Select a preset (or customize targets)
4. Click "Process"
5. Monitor progress in real-time
6. Download mix & master when complete

## 📦 Project Structure

```
mixmasterbis/
├── backend/              # Python backend
│   ├── api/             # FastAPI application
│   ├── audio_engine/    # Audio processing core
│   ├── tasks/           # Celery tasks
│   ├── ml_models/       # Neural models
│   └── config/          # Configuration & presets
├── frontend/            # Next.js frontend
├── nginx/               # Nginx configuration
├── monitoring/          # Prometheus & Grafana
└── docker-compose.yml   # Service orchestration
```

See [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md) for complete structure.

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-gpu.txt  # For GPU support

# Run API locally
uvicorn api.main:app --reload

# Run Celery worker locally
celery -A tasks.celery_app worker --loglevel=info
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 API Usage

### Create Job

```bash
curl -X POST http://localhost:8000/v1/jobs \
  -H "Content-Type: multipart/form-data" \
  -F "project_id=my-project" \
  -F "preset=Electro House" \
  -F "stems_meta=[{\"name\":\"kick.wav\",\"role\":\"kick\"}]" \
  -F "kick.wav=@/path/to/kick.wav"
```

### Check Status

```bash
curl http://localhost:8000/v1/jobs/{job_id}
```

### Download Results

```bash
# Mix premaster
curl -O http://localhost:8000/v1/jobs/{job_id}/download/mix

# Master final
curl -O http://localhost:8000/v1/jobs/{job_id}/download/master

# Report
curl -O http://localhost:8000/v1/jobs/{job_id}/download/report
```

## 🎛️ Presets

### Available Presets

- **Electro House**: LUFS −10, wide stereo, punchy kick
- **Pop**: LUFS −10, balanced, vocal-forward
- **Hip-Hop**: LUFS −8, heavy bass, tight drums
- **Rock**: LUFS −10, dynamic, guitar-focused
- **Streaming**: LUFS −14, conservative, broadcast-safe

### Custom Targets

```json
{
  "targets": {
    "lufs": -10,
    "ceiling_dbTP": -1.0,
    "width_pct": 120,
    "lra_max": 8.0
  },
  "options": {
    "respect_user_gains": false,
    "bypass_parallel_comp": false,
    "reference_track_url": "https://..."
  }
}
```

## 🛡️ Safety Guardrails

All processing includes automatic safety checks:

- **EQ Gain**: Max ±4 dB per band
- **Compression**: Average GR <3 dB per stem/bus
- **True Peak**: Always ≤ −1 dBTP
- **Stereo Width**: Capped at 140%
- **Mono Compatibility**: Correlation ≥ 0.1
- **Crest Factor**: Preserved to avoid over-compression

Failed checks trigger auto-adjustments (up to 3 iterations) or warnings in the report.

## 📈 Performance Benchmarks

Target latency for 4-minute track (12 stems):

| Stage     | Target    | Typical |
| --------- | --------- | ------- |
| Analysis  | 10-15s    | 12s     |
| Mixing    | 45-60s    | 52s     |
| Mastering | 20-30s    | 24s     |
| I/O       | 10-15s    | 11s     |
| **Total** | **≤120s** | **99s** |

_Benchmarked on NVIDIA RTX 3090, 32GB RAM_

## 🔍 Monitoring

### Grafana Dashboards

Access Grafana at http://localhost:3001 (default password in `.env`)

**Available Dashboards**:

- Job processing times
- Audio quality metrics (LUFS, TP, width)
- Worker utilization
- Error rates
- Queue depths

### Prometheus Metrics

Access Prometheus at http://localhost:9090

**Key Metrics**:

- `mixmaster_job_duration_seconds`
- `mixmaster_audio_lufs`
- `mixmaster_audio_true_peak`
- `mixmaster_worker_busy`
- `mixmaster_queue_length`

## 🐛 Troubleshooting

### GPU Not Detected

```bash
# Check NVIDIA driver
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Worker Crashes

```bash
# Check worker logs
docker-compose logs worker-gpu

# Reduce concurrency in docker-compose.yml
# Change --concurrency=2 to --concurrency=1
```

### Out of Memory

```bash
# Reduce chunk size in .env
CHUNK_SIZE_SECONDS=20  # Default: 25

# Or reduce max workers
MAX_WORKERS=2  # Default: 4
```

### Slow Processing

```bash
# Enable int8 quantization
ONNX_EXECUTION_PROVIDER=TensorrtExecutionProvider

# Reduce audio quality (not recommended)
SAMPLE_RATE=44100  # Default: 48000
```

## 📚 Documentation

- [Architecture](./ARCHITECTURE.md) - System design & data flow
- [Directory Structure](./DIRECTORY_STRUCTURE.md) - Code organization
- [API Reference](./docs/API.md) - Complete API documentation
- [Audio Engine](./docs/AUDIO_ENGINE.md) - Processing pipeline details
- [Presets Guide](./docs/PRESETS.md) - Creating custom presets
- [Deployment](./docs/DEPLOYMENT.md) - Production deployment guide

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

- **Spotify Pedalboard** - High-quality audio DSP
- **Essentia** - Music information retrieval
- **librosa** - Audio analysis
- **PyTorch** - Neural models
- **ONNX Runtime** - Fast inference
- **Celery** - Distributed task queue

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@mixmaster.pro

---

**Built with ❤️ for music producers worldwide**
