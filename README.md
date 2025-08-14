# AI Music Generator

A web platform for algorithmic music composition that balances creative control with intelligent automation. Users can generate original music by choosing style, mood, tempo, chord progressions, and instruments—or upload an unfinished MIDI to continue and complete it. The project supports multilingual UI (English, Traditional Chinese, Simplified Chinese) and exports to MIDI, MP3, and WAV for seamless DAW workflows.

Click here to see the final year report: https://github.com/yuuki321/fyp/fyp_finalreport.pdf

## Highlights

- Unified interface with progressive controls:
  - Simple “core” parameters for quick results
  - Advanced settings revealed as needed (no mode switching)
- Style control: Pop, Rock, Classical, Jazz, Electronic
- Mood control: Happy, Sad, Calm, Energetic, etc.
- Custom chord progressions and key/mode
- MIDI upload for continuation and reharmonization
- Multilingual UI: EN / 繁中 / 简中
- Project management: save, edit, delete, and re-generate
- Export: MIDI, MP3, WAV (MIDI via rule-based engine; audio via FluidSynth + FFmpeg)

## Tech Stack (as implemented in the final report)

- Frontend: React.js + Bootstrap (responsive, mobile-friendly)
- Backend: Python + Django REST Framework (JWT auth, Swagger docs)
- Database: SQLite (dev) / PostgreSQL (prod), SQLAlchemy/ORM
- Tasking: Celery + Redis for long-running generation jobs
- Music Engine: Hybrid rule-based + VAE (TensorFlow/PyTorch), pretty_midi, librosa
- Rendering: FluidSynth (SoundFont-based), optional FFmpeg for MP3
- Internationalization: i18next (frontend); JSON-based translations

Note on prototypes vs final implementation:
- Early prototype used Flask; final implementation (per report) migrated to Django REST for stronger auth and API ergonomics. If you are running an earlier prototype branch, you may see Flask and a run.py entrypoint; the final stack uses Django’s manage.py and REST endpoints.

## How It Works

- Parameter Processor: Interprets user inputs (style, mood, tempo, duration)
- Harmony: Chord progression generator with genre-aware templates or custom input
- Melody: Phrase-based melody with style-sensitive contour and voice-leading
- Rhythm: Style/mood-driven rhythmic patterns and percussion
- Arrangement: Instrumentation, dynamics, sectional structure, transitions
- Emotional mapping: Happy/Sad/Energetic/Calm → key/mode, tempo, register, dynamics
- Continuation: Analyze uploaded MIDI (key, tempo, motifs) and generate coherent next sections
- MIDI Engine: Proper note events, velocities, program/control changes
- Audio Rendering: FluidSynth + SoundFont → WAV; optional MP3 via FFmpeg

## Features (translated from the original brief)

- Quick start: generate foundational music with minimal inputs
- Fine-grained control: advanced parameters for experienced users
- Multiple genres and moods
- Custom chord progressions
- Multilingual UI (English, Simplified Chinese, Traditional Chinese)
- Project management (save/edit/delete)
- Export to MIDI, MP3, WAV

## System Requirements

- Python 3.9+ (3.8+ may work; report targets modern Python)
- FluidSynth (for MIDI-to-audio rendering)
- Optional: FFmpeg (for MP3 encoding)
- OS: Windows, macOS, or Linux
- RAM: 2 GB+ (8 GB+ recommended for AI models)
- Disk: 500 MB+ free (more if caching models/exports)
- Optional (final stack): Redis (task queue), PostgreSQL (production)

## Installation

Choose the path that matches the code you are running.

### A) Final stack (Django REST + React)

1) Backend (Django REST)
- Create and activate a virtual environment:
  ```
  python -m venv venv
  # Windows
  venv\Scripts\activate
  # macOS/Linux
  source venv/bin/activate
  ```
- Install dependencies:
  ```
  pip install -r backend/requirements.txt
  ```
- Configure environment:
  - Set database URL (SQLite dev or PostgreSQL prod)
  - Configure Redis URL if using Celery for async generation
- Migrate and run:
  ```
  python manage.py migrate
  python manage.py runserver
  ```
- (Optional) Start Celery worker:
  ```
  celery -A app worker -l info
  ```

2) Frontend (React)
- Install Node.js (LTS recommended), then:
  ```
  cd frontend
  npm install
  npm run start
  ```
- Access the UI at the indicated local URL.

3) Rendering tools
- Install FluidSynth and a GM SoundFont (e.g., FluidR3_GM.sf2), then configure its path.
- Install FFmpeg if you want MP3 export (see FFmpeg section below).

### B) Prototype path (Flask)

If you are running the early prototype (as in your original instructions):

- Ensure Python 3.8+ and FluidSynth are installed
- Create a virtual environment and install dependencies
- Start the app:
  ```
  # Windows
  venv\Scripts\activate
  python run.py

  # macOS/Linux
  source venv/bin/activate
  python run.py
  ```

## Package Notes

- macOS:
  - FluidSynth: `brew install fluidsynth`
  - FFmpeg: `brew install ffmpeg`
- Ubuntu/Debian:
  - FluidSynth: `sudo apt-get install fluidsynth`
  - FFmpeg: `sudo apt install ffmpeg`
- CentOS/RHEL:
  - FluidSynth: `sudo yum install fluidsynth`
  - FFmpeg: `sudo yum install ffmpeg` (or use EPEL/other repos)

## FFmpeg (for MP3 export)

FFmpeg provides source code and points to builds by platform.

- Official downloads and release notes:
  - https://ffmpeg.org/download.html
- Get the sources:
  ```
  git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
  ```
- Windows builds:
  - Windows builds from gyan.dev
  - Windows builds by BtbN
- macOS:
  - Static builds for macOS 64-bit
- Linux:
  - Use your distro packages or static builds

Optional signature verification (example from the official site):
```
curl https://ffmpeg.org/ffmpeg-devel.asc | gpg --import
gpg --verify ffmpeg-<version>.tar.xz.asc ffmpeg-<version>.tar.xz
```

Tip: After installing FFmpeg, ensure it is on PATH so the app can invoke it for MP3 encoding.

## Usage

- Create a project and set core parameters (style, mood, tempo, duration)
- Expand advanced settings to customize chords, key/mode, instruments, and sections
- Optionally upload an incomplete MIDI to continue/re-harmonize
- Generate, audition, tweak parameters, and regenerate as needed
- Export to MIDI (for DAW editing) or to WAV/MP3 for sharing

## Troubleshooting

1) FluidSynth not found
- Ensure FluidSynth is installed and available on PATH

2) No sound on playback
- Verify SoundFont path is correct
- Default example: `app/static/soundfonts/FluidR3_GM/FluidR3_GM.sf2`

3) Database errors
- For Django: run migrations again
- For prototype Flask: remove `app.db` and re-initialize/migrate

4) MP3 export fails
- Ensure FFmpeg is installed and on PATH
  - Windows: download from the official Download page and add to PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

## Roadmap (from the final report)

- Transformer-based long-form composition
- Real-time collaboration (multi-user sessions)
- Expanded genre coverage with specialized models
- Dedicated mobile apps (iOS/Android)
- Further performance optimizations and resource tuning
- Learning from user feedback for personalized generation
- Integrations to publish directly to streaming platforms

## Academic Context

- Hong Kong University of Science and Technology, 2024–2025
- Project: Development of a Website for Automatic Music Creation
- Approach: Hybrid rule-based + ML, unified progressive UI, MIDI-first workflow, multilingual support
- User testing: 15 participants; high satisfaction with UI clarity and musical quality

## License

MIT License. See LICENSE for details.

## Contact

- GitHub: https://github.com/yuuki321/fyp

Click [here]{https://yuuki321.github.io/fyp/fyp_finalreport.pdf} to see the final year report