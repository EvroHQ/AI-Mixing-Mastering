# 🎵 AI Mixing & Mastering in minutes

Upload your audio stems, let AI detect the genre, and get professional-quality mixing and mastering in minutes.

## ✨ Features

- **Multi-Stem Processing**: Handle up to 32 stems (WAV, AIFF, FLAC, MP3)
- **AI Genre Detection**: Automatic genre detection for optimal processing settings
- **Professional Mixing**: Intelligent stem balancing, EQ, compression, and panning
- **Studio-Grade Mastering**: Multi-band processing, loudness normalization, true-peak limiting
- **Fast Processing**: Complete mix & master in under 3 minutes
- **Multiple Genres**: House, Techno, EDM, Hip-Hop, Pop, Rock, R&B, Acoustic, and more

## 🎯 Quality Targets

| Genre          | Target LUFS | Use Case             |
| -------------- | ----------- | -------------------- |
| House / Techno | -8 to -9    | Club play            |
| EDM            | -9          | Festival / Streaming |
| Hip-Hop        | -10         | Streaming            |
| Pop            | -11         | Radio / Streaming    |
| Rock           | -12         | Dynamic preservation |
| Acoustic       | -14         | Natural dynamics     |

**All masters include:**

- True Peak: ≤ -1 dBTP
- Stereo Width: Optimized per genre
- Mono Compatibility: ≥ 0.1 correlation

## 🏗️ Architecture

```
Frontend (Next.js) → Backend (FastAPI) → Celery Workers → Backblaze B2 Storage
                          ↓
                    Redis (Queue)
```

### Tech Stack

- **Frontend**: Next.js 16, React 19, TailwindCSS
- **Backend**: Python, FastAPI, Celery
- **Storage**: Backblaze B2
- **Hosting**: Railway

## 📦 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI API
│   ├── celery_app.py        # Celery configuration
│   ├── audio_engine/        # Core audio processing
│   │   ├── analyzer/        # Audio analysis & genre detection
│   │   ├── mixer/           # Mixing engine
│   │   ├── masterer/        # Mastering engine
│   │   ├── presets/         # Genre presets
│   │   └── pipeline.py      # Main processing pipeline
│   ├── storage/             # B2 storage client
│   └── tasks/               # Celery tasks
│
└── frontend/
    ├── app/                 # Next.js pages
    │   ├── page.tsx         # Landing page
    │   ├── studio/          # Upload & processing studio
    │   └── contact/         # Contact page
    └── components/          # React components
```

---

**Built with ❤️ by EvroHQ for music producers worldwide**
