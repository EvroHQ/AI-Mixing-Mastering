# MixMaster Pro - Directory Structure

```
mixmasterbis/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py             # Job management endpoints
│   │   │   ├── presets.py          # Preset management
│   │   │   ├── audio.py            # Audio proxy endpoints
│   │   │   └── health.py           # Health checks
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── job.py              # Job models
│   │   │   ├── preset.py           # Preset models
│   │   │   └── user.py             # User models
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── job.py              # Job schemas
│   │       └── preset.py           # Preset schemas
│   │
│   ├── audio_engine/
│   │   ├── __init__.py
│   │   ├── analyzer/
│   │   │   ├── __init__.py
│   │   │   ├── spectral.py         # STFT/CQT/MFCC analysis
│   │   │   ├── loudness.py         # LUFS/LRA/True Peak
│   │   │   ├── musical.py          # Tempo/Key detection
│   │   │   ├── masking.py          # Spectral masking detection
│   │   │   ├── classifier.py       # Source classification
│   │   │   ├── embeddings.py       # PaSST/VGGish embeddings
│   │   │   └── pitch.py            # CREPE pitch detection
│   │   │
│   │   ├── mixer/
│   │   │   ├── __init__.py
│   │   │   ├── policy_model.py     # Neural policy model
│   │   │   ├── dsp_graph.py        # DSP processing graph
│   │   │   ├── stem_processor.py   # Per-stem processing
│   │   │   ├── bus_processor.py    # Bus processing
│   │   │   ├── sidechain.py        # Sidechain matrix
│   │   │   └── effects/
│   │   │       ├── __init__.py
│   │   │       ├── eq.py           # EQ processing
│   │   │       ├── compressor.py   # Compression
│   │   │       ├── deesser.py      # De-essing
│   │   │       ├── reverb.py       # Reverb
│   │   │       ├── delay.py        # Delay
│   │   │       └── stereo.py       # Stereo width
│   │   │
│   │   ├── masterer/
│   │   │   ├── __init__.py
│   │   │   ├── reference_match.py  # Reference matching
│   │   │   ├── eq.py               # Linear-phase EQ
│   │   │   ├── multiband_comp.py   # Multi-band compression
│   │   │   ├── parallel_comp.py    # Parallel compression
│   │   │   ├── saturator.py        # Saturation/clipping
│   │   │   ├── limiter.py          # True-Peak limiter
│   │   │   ├── stereo_safety.py    # M/S processing
│   │   │   └── qc_loop.py          # Auto-QC loop
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── audio_io.py         # Audio file I/O
│   │       ├── chunking.py         # Chunk processing
│   │       ├── overlap_add.py      # Overlap-add reconstruction
│   │       └── metrics.py          # Audio metrics calculation
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery configuration
│   │   ├── audio_processor.py      # Main processing task
│   │   ├── analysis_task.py        # Analysis stage
│   │   ├── mixing_task.py          # Mixing stage
│   │   └── mastering_task.py       # Mastering stage
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── minio_client.py         # MinIO/S3 client
│   │   └── b2_client.py            # Backblaze B2 client
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py           # Database connection
│   │   ├── models.py               # SQLAlchemy models
│   │   └── migrations/             # Alembic migrations
│   │
│   ├── ml_models/
│   │   ├── __init__.py
│   │   ├── policy/
│   │   │   ├── model.py            # Policy model definition
│   │   │   ├── train.py            # Training script
│   │   │   └── export_onnx.py      # ONNX export
│   │   ├── embeddings/
│   │   │   ├── passt.py            # PaSST embeddings
│   │   │   └── vggish.py           # VGGish embeddings
│   │   └── checkpoints/            # Model checkpoints
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Application settings
│   │   ├── presets/                # Audio presets
│   │   │   ├── electro_house.json
│   │   │   ├── pop.json
│   │   │   ├── hiphop.json
│   │   │   └── rock.json
│   │   └── safety_limits.py        # Safety constraints
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   ├── test_audio_engine/
│   │   ├── test_tasks/
│   │   └── fixtures/               # Test audio files
│   │
│   ├── scripts/
│   │   ├── benchmark.py            # Performance benchmarks
│   │   ├── validate_audio.py       # Audio quality validation
│   │   └── generate_report.py      # Report generation
│   │
│   ├── requirements.txt            # Python dependencies
│   ├── requirements-gpu.txt        # GPU-specific dependencies
│   ├── Dockerfile                  # API container
│   ├── Dockerfile.worker           # Worker container
│   └── README.md
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # Landing page
│   │   ├── studio/
│   │   │   └── page.tsx            # Studio page
│   │   └── layout.tsx
│   ├── components/
│   │   ├── UploadWidget.tsx        # Multi-stem upload
│   │   ├── AudioPlayer.tsx         # Audio player
│   │   ├── ProcessingStatus.tsx    # Status display
│   │   ├── PresetSelector.tsx      # Preset selection
│   │   ├── TargetControls.tsx      # LUFS/width controls
│   │   └── ReportViewer.tsx        # Report visualization
│   ├── lib/
│   │   └── api.ts                  # API client
│   └── package.json
│
├── nginx/
│   ├── nginx.conf                  # Nginx configuration
│   └── Dockerfile
│
├── docker-compose.yml              # Development compose
├── docker-compose.prod.yml         # Production compose
├── .env.example
├── ARCHITECTURE.md
└── README.md
```

## Key Directories Explained

### `/backend/audio_engine/`

Core audio processing logic organized by stage:

- **analyzer**: Feature extraction and analysis
- **mixer**: Neural + DSP mixing engine
- **masterer**: Mastering chain
- **utils**: Shared utilities

### `/backend/ml_models/`

Neural network models:

- **policy**: Transformer-based parameter prediction
- **embeddings**: Audio embedding models
- **checkpoints**: Trained model weights

### `/backend/tasks/`

Celery tasks for distributed processing:

- Main orchestration task
- Stage-specific tasks (analysis, mixing, mastering)

### `/backend/config/presets/`

Genre-specific mixing presets:

- Target LUFS levels
- EQ curves
- Compression ratios
- Reverb/delay settings

### `/frontend/components/`

React components for UI:

- Multi-stem upload with progress
- Real-time status updates
- Audio comparison players
- Visual report display
