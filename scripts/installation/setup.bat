@echo off
setlocal
REM chcp 65001 >nul 2>nul

REM Navigate to project root
pushd "%~dp0\..\.."

echo [INFO] Starting Personal Guru Setup...

REM Check Conda
where conda >nul 2>nul
if %errorlevel% neq 0 goto :no_conda

REM Initialize conda for batch scripts
call conda activate base
if %errorlevel% neq 0 goto :conda_init_fail

REM Check FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 goto :ffmpeg_ok

echo.
echo [WARNING] FFmpeg is not installed. It is required for audio processing.
set /p install_ffmpeg="Do you want to install it now using winget? [y/N]: "
if /i not "%install_ffmpeg%"=="y" goto :ffmpeg_skip
echo [INFO] Attempting to install FFmpeg via winget...
winget install ffmpeg --accept-source-agreements --accept-package-agreements
if %errorlevel% neq 0 echo [ERROR] Failed to install FFmpeg via winget. Please install manually from https://ffmpeg.org/download.html
if %errorlevel% equ 0 echo [SUCCESS] FFmpeg installed successfully.
goto :ffmpeg_done

:ffmpeg_skip
echo [WARNING] Skipping FFmpeg installation. Audio features may not work.
goto :ffmpeg_done

:ffmpeg_ok
echo [INFO] FFmpeg is already installed.

:ffmpeg_done

REM Interactive Prompts
echo.
echo Select Installation Mode:
echo 1. Hybrid Mode (Docker for DB - Recommended for Developers)
echo 2. Local Lite Mode (No Docker - Easiest Setup)

:ask_mode
set /p mode_choice="Enter choice [1/2]: "
if "%mode_choice%"=="1" goto :mode_selected
if "%mode_choice%"=="2" goto :mode_selected

echo [ERROR] Invalid choice. Please enter 1 or 2.
goto :ask_mode

:mode_selected

if "%mode_choice%"=="2" goto :setup_local_mode

echo [INFO] Hybrid Mode selected.
set local_mode=n

REM Configure .env for Hybrid Mode
if not exist .env goto :create_env_hybrid
echo [WARNING] Existing .env file found.
set /p overwrite_env_hybrid="Do you want to overwrite it with default settings? [y/N]: "
if /i not "%overwrite_env_hybrid%"=="y" goto :skip_env_hybrid
:create_env_hybrid
copy .env.example .env
echo [INFO] Created/Overwritten .env from example.
:skip_env_hybrid
echo.
goto :env_check

:setup_local_mode
echo [INFO] Local Mode selected. Using SQLite and Local Audio.
set local_mode=y
set install_tts=n
set start_db=n

if not exist .env goto :create_env_fresh
echo [WARNING] Existing .env file found.
set /p overwrite_env="Do you want to overwrite it with default Local Mode settings? (Recommended) [y/N]: "
if /i "%overwrite_env%"=="y" goto :create_env_fresh
echo [INFO] Keeping existing .env file.
goto :check_overrides

:create_env_fresh
copy .env.example .env
echo [INFO] Created/Overwritten .env from example.

:check_overrides
"%ENV_PYTHON%" -c "import sys; content = open('.env', 'r', encoding='utf-8', errors='ignore').read(); sys.exit(0 if '# Local Mode Overrides' in content else 1)"
if not errorlevel 1 (
    echo [INFO] .env already contains Local Mode overrides. Skipping update.
    goto :env_check
)

echo. >> .env
echo # Local Mode Overrides >> .env
echo DATABASE_URL=sqlite:///site.db >> .env
echo TTS_PROVIDER=native >> .env
echo STT_PROVIDER=native >> .env
echo [INFO] Updated .env for Local Mode (SQLite + Native Audio).

:env_check

REM Check if environment already exists
call conda info --envs | findstr /B /C:"Personal-Guru " >nul 2>nul
if %errorlevel% equ 0 goto :env_exists

REM Create Environment
echo [INFO] Creating conda environment 'Personal-Guru' with Python 3.11...
call conda create -n Personal-Guru python=3.11 -y
if %errorlevel% neq 0 goto :env_create_fail
goto :env_verify

:env_exists
echo [INFO] Environment 'Personal-Guru' already exists. Skipping creation.

:env_verify
REM Verify environment was created
call conda info --envs | findstr /B /C:"Personal-Guru " >nul 2>nul
if %errorlevel% neq 0 goto :env_not_found

REM Activate the environment (Just in case, but we will use direct path)
echo [INFO] Activating Personal-Guru environment...
call conda activate Personal-Guru
if %errorlevel% neq 0 echo [WARNING] Conda activate failed. Will rely on direct python path.

REM Resolve Python Path
echo [INFO] Resolving Python executable path...
for /f "usebackq tokens=*" %%i in (`conda run -n Personal-Guru python -c "import sys; print(sys.executable)"`) do set ENV_PYTHON=%%i
echo [INFO] Using Python: %ENV_PYTHON%

REM Install Dependencies
echo [INFO] Installing Dependencies from pyproject.toml...
if /i "%local_mode%"=="y" (
    "%ENV_PYTHON%" -m pip install -e .[local]
) else (
    echo [INFO] Installing development dependencies...
    "%ENV_PYTHON%" -m pip install -e .[dev]
)
if %errorlevel% neq 0 echo [WARNING] Some dependencies may have failed to install.

REM Install pre-commit hooks
echo [INFO] Installing pre-commit hooks...
"%ENV_PYTHON%" -m pre_commit install
if %errorlevel% neq 0 echo [WARNING] Failed to install pre-commit hooks.

REM Optional TTS (Removed from setup)


REM Install GTK3 for WeasyPrint (required for PDF generation on Windows)
echo.
echo [INFO] Installing GTK3 runtime for WeasyPrint (PDF generation)...
call conda install -n Personal-Guru -c conda-forge gtk3 -y
if %errorlevel% neq 0 echo [WARNING] GTK3 installation via conda failed. WeasyPrint PDF generation may not work.

REM Database Setup
echo.
if /i "%local_mode%"=="y" goto :local_db_setup

set /p start_db="Start Database via Docker now? [Y/n]: "
if /i "%start_db%"=="n" goto :skip_db
goto :run_docker_db

:local_db_setup
echo [INFO] Using Local SQLite Database.
echo [INFO] Initializing SQLite Database...
"%ENV_PYTHON%" scripts\update_database.py
set start_db=n
goto :end_db_setup

:run_docker_db
echo [INFO] Starting Database...
docker compose up -d db
echo [INFO] Waiting for Database to be ready...
ping -n 6 127.0.0.1 >nul

REM Configure .env for Hybrid Mode (Postgres)
"%ENV_PYTHON%" -c "import sys; content = open('.env', 'r', encoding='utf-8', errors='ignore').read(); sys.exit(0 if 'sqlite:///site.db' in content else 1)"
if %errorlevel% equ 0 (
    echo [INFO] Switching .env to use PostgreSQL via Docker...
    echo. >> .env
    echo # Hybrid Mode Overrides >> .env
    echo DATABASE_URL=postgresql://postgres:postgres@localhost:5433/personal_guru >> .env
)

echo [INFO] Initializing/Updating Database Tables...
"%ENV_PYTHON%" scripts\update_database.py

:ask_tts
echo.
set /p run_tts="Do you want to run local Speaches/Kokoro (TTS/STT) via Docker? (Large download ~5GB) [y/N]: "
if /i not "%run_tts%"=="y" goto :skip_tts

echo [INFO] Starting Speaches (TTS/STT)...
docker compose --profile tts up -d speaches

echo [INFO] Waiting for TTS Server to start (15s)...
ping -n 16 127.0.0.1 >nul

echo [INFO] Downloading Kokoro-82M model...
docker compose exec speaches uv tool run speaches-cli model download speaches-ai/Kokoro-82M-v1.0-ONNX

echo [INFO] Downloading Faster Whisper Medium model (STT)...
docker compose exec speaches uv tool run speaches-cli model download Systran/faster-whisper-medium.en

echo [SUCCESS] TTS/STT Services Ready.

REM Update .env to use externalapi for Hybrid Mode
"%ENV_PYTHON%" -c "import sys; content = open('.env', 'r', encoding='utf-8', errors='ignore').read(); sys.exit(0 if 'TTS_PROVIDER=externalapi' in content else 1)"
if %errorlevel% neq 0 (
    echo. >> .env
    echo # Hybrid Mode Audio >> .env
    echo TTS_PROVIDER=externalapi >> .env
    echo TTS_BASE_URL=http://localhost:8969/v1 >> .env
    echo STT_PROVIDER=externalapi >> .env
    echo STT_BASE_URL=http://localhost:8969/v1 >> .env
)

:skip_tts

:end_db_setup
:skip_db

echo.
echo [SUCCESS] Setup Complete!
echo.
echo The setup for environment 'Personal-Guru' is complete.
echo To run the application:
echo   python run.py
echo.
echo If you open a new terminal, first run:
echo   conda activate Personal-Guru
echo.
goto :end

:no_conda
echo [ERROR] Conda is not installed. Please install Miniconda or Anaconda first.
pause
exit /b 1

:conda_init_fail
echo [ERROR] Failed to initialize conda. Make sure conda init has been run.
pause
exit /b 1

:env_create_fail
echo.
echo [ERROR] Failed to create conda environment.
echo         This may be due to Conda Terms of Service not being accepted.
echo.
echo Please run the following commands to accept the TOS:
echo     conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
echo     conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
echo     conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
echo.
echo Then re-run this setup script.
pause
exit /b 1

:env_not_found
echo [ERROR] Environment 'Personal-Guru' does not exist. Setup cannot continue.
pause
exit /b 1

:env_activate_fail
echo [ERROR] Failed to activate Personal-Guru environment.
pause
exit /b 1

:end
endlocal
