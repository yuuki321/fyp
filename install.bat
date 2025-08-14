@echo off
echo ========================================
echo    AI Music Generator Installer
echo ========================================

REM Check Python version
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Please install Python 3.8 or newer first
    exit /b 1
)

REM Check for FluidSynth
where fluidsynth >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: FluidSynth not detected
    echo Please visit https://github.com/FluidSynth/fluidsynth/releases to download and install FluidSynth
    echo After installing, make sure to add FluidSynth to your system PATH
    set /p CONTINUE="Continue installation? (Y/N): "
    if /I "%CONTINUE%" NEQ "Y" exit /b 1
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file
if not exist .env (
    echo Creating environment configuration file...
    copy .env.example .env
    REM Generate random key
    for /f "tokens=*" %%a in ('python -c "import secrets; print(secrets.token_hex(16))"') do set RANDOM_KEY=%%a
    REM Replace key using PowerShell
    powershell -Command "(Get-Content .env) -replace 'your-secret-key-here', '%RANDOM_KEY%' | Set-Content .env"
)

REM Initialize database
echo Initializing database...
flask db upgrade

echo ========================================
echo Installation complete!
echo To start the application, run these commands:
echo 1. call venv\Scripts\activate
echo 2. python run.py
echo ========================================

pause