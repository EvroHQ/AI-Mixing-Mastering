# MixMaster Pro - Architecture Documentation

## 🎯 System Overview

Professional audio mixing and mastering pipeline capable of processing up to 12 stems with studio-grade quality.

**Performance Target**: ≤120 seconds for 4-minute track
**Quality Target**: Studio-grade output with safety constraints

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  (Next.js Frontend + Upload Widget + Audio Players)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway (Nginx)                        │
│  - Chunked uploads (up to 500MB)                           │
│  - Rate limiting                                             │
│  - SSL termination                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Application                           │
│  - Job management                                            │
│  - Authentication                                            │
│  - Preset management                                         │
│  - Status polling                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Job Queue (Redis + Celery)                      │
│  - GPU worker pool                                           │
│  - Priority queues                                           │
│  - Result backend                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Audio Processing Engine                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Analysis Stage (10-15s)                         │   │
│  │     - Multi-resolution STFT/CQT/MFCC                │   │
│  │     - LUFS/LRA/True Peak/Crest Factor               │   │
│  │     - Tempo/Key detection                           │   │
│  │     - Spectral masking analysis                     │   │
│  │     - Source classification                         │   │
│  │     - PaSST/VGGish embeddings                       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. Neural Mixing Engine (45-60s)                   │   │
│  │     - Policy model (PyTorch → ONNX)                 │   │
│  │     - Parameter prediction                          │   │
│  │     - DSP graph execution (Pedalboard)              │   │
│  │     - Per-stem processing                           │   │
│  │     - Bus processing                                │   │
│  │     - Sidechain matrix                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. Mastering Engine (20-30s)                       │   │
│  │     - Reference matching                            │   │
│  │     - Linear-phase EQ                               │   │
│  │     - Multi-band compression                        │   │
│  │     - Parallel compression                          │   │
│  │     - Saturation/Clipping                           │   │
│  │     - True-Peak limiting                            │   │
│  │     - Auto-QC loop                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Storage Layer (MinIO/B2)                        │
│  - Input stems                                               │
│  - Mix premaster                                             │
│  - Master final                                              │
│  - Reports & previews                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            Database (PostgreSQL)                             │
│  - Jobs metadata                                             │
│  - User presets                                              │
│  - Processing history                                        │
│  - Analytics                                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

### Backend

- **FastAPI**: REST API framework
- **Celery**: Distributed task queue
- **Redis**: Job queue & caching
- **PostgreSQL**: Metadata storage
- **Docker**: Containerization
- **Nginx**: Reverse proxy & upload handling

### Audio Processing

- **torchaudio**: PyTorch audio I/O
- **librosa**: Audio analysis
- **Essentia**: Music information retrieval
- **pyloudnorm**: Loudness normalization
- **Pedalboard**: High-quality DSP (Spotify)
- **ONNX Runtime**: Neural model inference
- **CREPE**: Pitch detection
- **PaSST/VGGish**: Audio embeddings

### Future (Phase 2)

- **JUCE**: C++ audio framework
- **pybind11**: Python-C++ bindings
- **TensorRT**: GPU-accelerated inference

## 📊 Processing Pipeline

### 1. Analysis Stage (10-15s)

**Input**: Up to 12 stems (24-bit WAV/AIFF, 44.1/48 kHz)

**Extracted Features**:

- Multi-resolution spectrograms (STFT, CQT, MFCC)
- Loudness metrics (LUFS, LRA, True Peak, Crest Factor)
- Musical features (Tempo, Key, Beat grid)
- Spectral masking detection
- Source classification (kick, snare, bass, vocals, etc.)
- Audio embeddings for reference matching
- Pitch analysis for vocal processing

**Output**: Feature vectors + metadata JSON

### 2. Neural Mixing Engine (45-60s)

**Policy Model** (Transformer-based):

- Input: Concatenated feature vectors from all stems
- Output: Mixing parameters for each stem

**Predicted Parameters**:

- Fader levels & pan positions
- Target EQ curves (gain/Q/frequency)
- Compression ratios & thresholds
- Sidechain relationships
- Reverb/delay send levels
- Stereo width caps

**DSP Chain per Stem**:

1. Gain staging (−6 dBFS headroom)
2. HPF/LPF intelligent filters
3. Dynamic EQ (masking reduction)
4. De-esser (vocal stems)
5. Compressor (ratio ~2:1, GR <3 dB)
6. Pan & width (psychoacoustic)
7. Sends (reverb + delay)

**Bus Processing**:

- **Drum Bus**: Glue compression, transient enhancement
- **Music Bus**: Low-mid cleanup (200–350 Hz), air boost
- **Vocal Bus**: Parallel compression, presence shelf

**Sidechain Matrix**:

- Kick → Bass (40–120 Hz, look-ahead 5–10 ms)
- Lead Vocal → Music (0.5–1.5 dB broadband duck)

### 3. Mastering Engine (20-30s)

**Processing Chain**:

1. Reference matching (embedding distance)
2. Linear-phase EQ (±3 dB max)
3. Multi-band compression (3–4 bands)
4. Parallel compression (optional density)
5. Saturation/Soft clipping (8× oversampling)
6. True-Peak limiter (−1 dBTP ceiling)
7. LUFS targeting (−14 / −10 / −8)
8. Stereo M/S safety processing
9. Auto-QC loop with micro-adjustments

**Safety Constraints**:

- True Peak ≤ −1 dBTP
- Stereo width ≤ 140%
- Mono correlation ≥ 0.1
- Max EQ gain ±4 dB
- Average GR <3 dB per stem/bus
- Crest factor preservation

## 🚀 Performance Optimization

### Parallelization

- Chunk processing (20–30s windows, 200–500ms overlap)
- Parallel stem processing
- Serial bus/post chain
- Spectrogram caching

### GPU Acceleration

- ONNX Runtime with CUDA
- TensorRT int8 quantization
- Batch processing where possible

### Target Latency Breakdown

- Analysis: 10–15s
- Mixing: 45–60s
- Mastering: 20–30s
- I/O: 10–15s
- **Total**: ≤120s for 4-minute track

## 📡 API Specification

### POST /v1/jobs

Create new mixing/mastering job

**Request**:

```json
{
  "project_id": "abc123",
  "preset": "Electro House",
  "targets": {
    "lufs": -10,
    "ceiling_dbTP": -1.0,
    "width_pct": 120
  },
  "options": {
    "respect_user_gains": false,
    "bypass_parallel_comp": false
  },
  "stems_meta": [
    { "name": "kick.wav", "role": "kick" },
    { "name": "bass.wav", "role": "bass" },
    { "name": "leadvox.wav", "role": "lead_vocal" },
    { "name": "drums.wav", "role": "drums_bus" },
    { "name": "keys.wav", "role": "keys" },
    { "name": "gtr.wav", "role": "guitar" }
  ]
}
```

**Response**:

```json
{
  "job_id": "job_xyz789",
  "status": "queued",
  "created_at": "2025-12-10T20:00:00Z"
}
```

### GET /v1/jobs/{id}

Get job status and results

**Response**:

```json
{
  "job_id": "job_xyz789",
  "status": "complete",
  "progress": 100,
  "created_at": "2025-12-10T20:00:00Z",
  "completed_at": "2025-12-10T20:02:00Z",
  "results": {
    "mix_premaster_url": "https://storage/mix_premaster.wav",
    "master_final_url": "https://storage/master_final.wav",
    "report_url": "https://storage/report.json",
    "preview_ab_url": "https://storage/preview_AB.mp3"
  },
  "metrics": {
    "lufs": -10.2,
    "lra": 6.5,
    "true_peak": -1.0,
    "crest_factor": 8.2,
    "stereo_width": 118,
    "mono_correlation": 0.85,
    "detected_bpm": 128,
    "detected_key": "A minor"
  }
}
```

## 📋 Output Report Format

```json
{
  "job_id": "job_xyz789",
  "processing_time_seconds": 95.3,
  "input_analysis": {
    "total_stems": 6,
    "sample_rate": 48000,
    "bit_depth": 24,
    "duration_seconds": 245.5,
    "detected_bpm": 128,
    "detected_key": "A minor",
    "stems": [
      {
        "name": "kick.wav",
        "role": "kick",
        "lufs": -12.5,
        "true_peak": -3.2,
        "crest_factor": 12.1
      }
    ]
  },
  "mixing_report": {
    "avg_gain_reduction_db": {
      "drum_bus": 2.1,
      "music_bus": 1.8,
      "vocal_bus": 2.5
    },
    "sidechain_applied": [
      { "source": "kick", "target": "bass", "avg_gr_db": 1.2 },
      { "source": "lead_vocal", "target": "music", "avg_gr_db": 0.8 }
    ],
    "stereo_width_avg": 115
  },
  "mastering_report": {
    "lufs_integrated": -10.2,
    "lufs_target": -10.0,
    "lra": 6.5,
    "true_peak_dbTP": -1.0,
    "crest_factor": 8.2,
    "stereo_width_pct": 118,
    "mono_correlation": 0.85,
    "eq_applied": {
      "low_shelf_db": 1.2,
      "presence_db": 0.8,
      "air_db": 1.5
    },
    "compression": {
      "avg_gr_db": 2.3,
      "max_gr_db": 4.1
    },
    "limiting": {
      "avg_gr_db": 1.8,
      "max_gr_db": 3.2
    }
  },
  "qc_results": {
    "passed": true,
    "checks": {
      "lufs_in_range": true,
      "true_peak_safe": true,
      "stereo_width_safe": true,
      "mono_compatible": true,
      "crest_factor_preserved": true
    },
    "warnings": [],
    "notes": "All quality checks passed"
  }
}
```

## 🛡️ Safety Guardrails

### Audio Integrity Constraints

- Max EQ gain: ±4 dB per band
- Average GR: <3 dB per stem/bus
- True Peak: ≤ −1 dBTP
- Stereo width: ≤ 140%
- Mono correlation: ≥ 0.1
- Crest factor: Preserved (no over-compression)

### Auto-QC Loop

If any metric is out of tolerance:

1. Identify problematic parameter
2. Apply micro-adjustment (±0.5 dB)
3. Re-measure
4. Repeat up to 3 iterations
5. Log warnings if still out of range

## 🐳 Deployment

### Docker Compose Services

- `api`: FastAPI application
- `worker-gpu`: Celery worker with GPU access
- `redis`: Job queue & cache
- `postgres`: Metadata database
- `minio`: Object storage (S3-compatible)
- `nginx`: Reverse proxy & upload handler

### Health Checks

- API: `/health` endpoint
- Worker: Celery inspect
- Redis: PING command
- PostgreSQL: SELECT 1
- MinIO: Bucket list

### Monitoring

- Prometheus metrics
- Grafana dashboards
- Latency tracking
- Audio quality metrics
- Error rates

## 📈 Scalability

### Horizontal Scaling

- Multiple GPU workers
- Load balancing via Nginx
- Redis Cluster for high availability
- PostgreSQL read replicas

### Vertical Scaling

- GPU memory optimization
- Batch processing
- Model quantization (int8)
- Efficient DSP algorithms

## 🔄 Migration Path

### Phase 1 (MVP - Current)

- Python DSP (Pedalboard)
- ONNX policy model
- Basic mixing parameters
- Single GPU worker

### Phase 2 (Production)

- C++/JUCE DSP graph
- Advanced neural models
- Multi-GPU support
- Real-time preview
- Advanced presets

### Phase 3 (Enterprise)

- Cloud deployment
- Auto-scaling
- Multi-region
- Advanced analytics
- API monetization
