# AI Music Creator — Installation Guide

This document provides step-by-step instructions for installing and running the AI Music Creator.

## System Requirements

- Python 3.7+
- FluidSynth 2.0+
- Database (SQLite/PostgreSQL)
- A modern web browser

## Installation Steps

### 1) Unzip the package

Extract the downloaded zip file to a directory of your choice.

```bash
unzip ai_music_generator_v*.zip -d ai_music_creator
cd ai_music_creator
```

### 2) Create a virtual environment

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Install FluidSynth

- macOS:
  ```bash
  brew install fluidsynth
  ```

- Linux (Ubuntu/Debian):
  ```bash
  sudo apt-get install fluidsynth
  ```

- Windows:
  Download and install FluidSynth from the official releases page:
  https://github.com/FluidSynth/fluidsynth/releases

### 5) Download a SoundFont

Follow the instructions in `app/static/soundfonts/README.txt` to download a SoundFont.

- Quick guide:
  ```bash
  # Create directories
  mkdir -p app/static/soundfonts/FluidR3_GM

  # Download FluidR3_GM.sf2 (Method 1)
  # Download from https://musical-artifacts.com/artifacts/files/fluid-r3-soundfont.zip and extract
  # Then place FluidR3_GM.sf2 into app/static/soundfonts/FluidR3_GM/

  # Or download a single-instrument SoundFont (Method 2)
  mkdir -p app/static/soundfonts/acoustic_grand_piano
  curl -L "https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/acoustic_grand_piano-mp3.js" \
       -o app/static/soundfonts/acoustic_grand_piano/acoustic_grand_piano-mp3.js
  ```

### 6) Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7) Run the application

```bash
python run.py
```

Open http://127.0.0.1:2401 in your browser to use the app.

## Troubleshooting

### 1) FluidSynth-related errors

If you see “Missing dependencies” or “FluidSynth not initialized”:
- Ensure FluidSynth is correctly installed
- Confirm the SoundFont file is placed at the correct path
- Check that you have sufficient permissions to access these files

### 2) Database initialization errors

If you run into migration/setup issues:
```bash
# Remove the migrations folder and re-initialize
rm -rf migrations
flask db init
flask db migrate -m "Fresh migration"
flask db upgrade
```

### 3) Port already in use

If port 2401 is occupied, change the port configuration in `run.py`.

### 4) Email validation error

If you encounter “Install 'email_validator' for email validation support”:
```bash
pip install email_validator
```
This is a dependency required by the registration form’s email validator. If you installed from requirements.txt successfully, you should not see this error.