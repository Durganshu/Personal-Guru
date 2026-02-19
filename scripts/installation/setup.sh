#!/bin/bash
set -e

# Ensure script runs from project root (scripts/installation -> project root)
cd "$(dirname "$0")/../.."

echo "🚀 Starting Personal Guru Setup..."

# --- Function Definitions ---

check_conda() {
    if ! command -v conda &> /dev/null; then
        echo "❌ Conda is not installed. Please install Miniconda or Anaconda first."
        exit 1
    fi
}

check_env_exists() {
    if conda env list | grep -q "Personal-Guru"; then
        return 0
    else
        return 1
    fi
}

# --- Main Script ---

check_system_deps() {
    echo "🔍 Checking system dependencies..."
    PACKAGES="ffmpeg"

    # Check for pkg-config (required for building av)
    if ! command -v pkg-config &> /dev/null; then
        echo "⚠️  pkg-config is missing."
        PACKAGES="$PACKAGES pkg-config"
    fi

    # Check for FFmpeg (runtime)
    if ! command -v ffmpeg &> /dev/null; then
        echo "⚠️  FFmpeg is missing."
    else
        echo "✅ FFmpeg is installed."
        # If we just need runtime ffmpeg, we might be good, but for building 'av' we need dev libs on Linux
    fi

    # On Linux, usually need dev headers for av build if no wheel
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # We can't easily check for libs existence without pkg-config or dpkg, so we might just ensure they are installed if user agrees
        echo "⚠️  On Linux, 'av' python package requires FFmpeg development libraries and pkg-config to build."
    fi

    echo "Do you want to install missing system dependencies (ffmpeg, pkg-config, dev libs)? [y/N]: "
    read -p "" install_deps

    if [[ "$install_deps" =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if command -v apt &> /dev/null; then
                echo "📦 Installing System Dependencies via apt..."
                sudo apt update && sudo apt install -y ffmpeg pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
            elif command -v dnf &> /dev/null; then
                echo "📦 Installing System Dependencies via dnf..."
                sudo dnf install -y ffmpeg pkgconfig ffmpeg-devel
            elif command -v pacman &> /dev/null; then
                echo "📦 Installing System Dependencies via pacman..."
                sudo pacman -S ffmpeg pkgconf
            else
                echo "❌ Could not detect package manager. Please install ffmpeg and pkg-config manually."
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
             if command -v brew &> /dev/null; then
                echo "📦 Installing Dependencies via Homebrew..."
                brew install ffmpeg pkg-config
             else
                echo "❌ Homebrew not found. Please install ffmpeg and pkg-config manually."
             fi
        else
            echo "❌ OS not supported for auto-install. Please install dependencies manually."
        fi
    else
        echo "⚠️  Skipping system dependency installation. 'pip install' may fail if wheels are missing."
    fi
}

# --- Main Script ---

check_conda
check_system_deps

# Interactive Prompts

env_opts="python=3.11"



echo ""
echo "Select Installation Mode:"
echo "1) Hybrid Mode (Docker for DB - Recommended for Developers)"
echo "2) Local Lite Mode (No Docker - Easiest Setup)"

while true; do
    read -p "Enter choice [1/2]: " mode_choice
    if [[ "$mode_choice" == "1" || "$mode_choice" == "2" ]]; then
        break
    else
        echo "❌ Invalid choice. Please enter '1' or '2'."
    fi
done

if [[ "$mode_choice" == "2" ]]; then
    local_mode="y"
    echo "✅ Local Mode selected. Using SQLite and Local Audio providers."
    install_tts="n"
    start_db="n"

    # Configure .env for Local Mode
    if [ -f .env ]; then
        echo "⚠️  Existing .env file found."
        echo "Do you want to overwrite it with default Local Mode settings? (Recommended) [y/N]: "
        read -p "" overwrite_env
        if [[ "$overwrite_env" =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo "📝 Overwrote .env with example."
        else
            echo "ℹ️  Keeping existing .env file."
        fi
    else
        cp .env.example .env
        echo "📝 Created .env from example."
    fi

    # Check if Local Mode Overrides already exist to avoid duplication
    if ! grep -q "# Local Mode Overrides" .env; then
        echo "" >> .env
        echo "# Local Mode Overrides" >> .env
        echo "DATABASE_URL=sqlite:///site.db" >> .env
        echo "TTS_PROVIDER=native" >> .env
        echo "STT_PROVIDER=native" >> .env
        echo "✅ Updated .env for Local Mode (SQLite + Native Audio)."
    else
        echo "ℹ️  .env already contains Local Mode overrides. Skipping update."
    fi

elif [[ "$mode_choice" == "1" ]]; then
    local_mode="n"
    echo "✅ Hybrid Mode selected."

    # Configure .env for Hybrid Mode
    if [ -f .env ]; then
        echo "⚠️  Existing .env file found."
        read -p "Do you want to overwrite it with default settings? [y/N]: " overwrite_env
        if [[ "$overwrite_env" =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo "📝 Overwrote .env with example."
        else
            echo "ℹ️  Keeping existing .env file."
        fi
    else
        cp .env.example .env
        echo "📝 Created .env from example."
    fi
    echo ""
fi

# Environment Creation
if check_env_exists; then
    echo "✅ Conda environment 'Personal-Guru' already exists."
else
    echo "📦 Creating Conda environment..."
    conda create -n Personal-Guru $env_opts -y
fi

# Install Dependencies
echo "📦 Installing Dependencies from pyproject.toml..."
ENV_PYTHON=$(conda run -n Personal-Guru which python)

# Core Install
if [[ "$local_mode" =~ ^[Yy]$ ]]; then
    # Local Mode includes local dependencies (TTS/STT)
    $ENV_PYTHON -m pip install -e ".[local]"
else
    # Standard Mode (Core only) -> Now enforcing dev deps for everyone per requirement
    echo "📦 Installing development dependencies..."
    $ENV_PYTHON -m pip install -e ".[dev]"

    # Ensure pre-commit is installed explicitly (in case of cache issues)
    $ENV_PYTHON -m pip install pre-commit

    # Install pre-commit hooks
    echo "🪝 Installing pre-commit hooks..."
    if $ENV_PYTHON -m pre_commit --version &> /dev/null; then
        $ENV_PYTHON -m pre_commit install
    else
        echo "⚠️  pre-commit not found. Skipping hook installation."
    fi
fi

# Optional TTS (Removed)


# Database Setup
echo ""
if [[ "$local_mode" =~ ^[Yy]$ ]]; then
    echo "✅ Using Local SQLite Database."
    # Initialize SQLite DB
    echo "🗄️  Initializing SQLite Database..."
    $ENV_PYTHON scripts/update_database.py
    start_db="n"
else
    # Hybrid Mode: Ask about services
    echo "🐳 Hybrid Mode Setup"
    echo "----------------------"

    # --- Database Setup ---
    read -p "Start Database via Docker now? [Y/n]: " start_db
    if [[ "$start_db" =~ ^[Nn]$ ]]; then
        echo "Using existing DB or manual setup..."
    else
        if command -v docker &> /dev/null; then
            echo "🐳 Starting Database..."
            docker compose up -d db

            echo "⏳ Waiting for Database to be ready..."
            sleep 5

            # Configure .env for Hybrid Mode (Postgres)
            if grep -q "sqlite:///site.db" .env; then
                echo "ℹ️  Switching .env to use PostgreSQL (Docker)..."
                echo "" >> .env
                echo "# Hybrid Mode Overrides" >> .env
                echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5433/personal_guru" >> .env
            fi

            echo "🗄️  Initializing/Updating Database Tables..."
            $ENV_PYTHON scripts/update_database.py
        else
            echo "❌ Docker not found. Skipping DB start."
        fi
    fi

    echo ""

    # --- TTS/STT Setup ---
    read -p "Do you want to run local Speaches/Kokoro (TTS/STT) via Docker? (Large download ~5GB) [y/N]: " run_tts
    if [[ "$run_tts" =~ ^[Yy]$ ]]; then
        if command -v docker &> /dev/null; then
            echo "🎤 Starting Speaches (TTS/STT)..."
            docker compose --profile tts up -d speaches

            echo "⏳ Waiting for TTS Server to start (15s)..."
            sleep 15

            echo "⬇️  Downloading Kokoro-82M model..."
            docker compose exec speaches uv tool run speaches-cli model download speaches-ai/Kokoro-82M-v1.0-ONNX
            echo "⬇️  Downloading Faster Whisper Medium model (STT)..."
            docker compose exec speaches uv tool run speaches-cli model download Systran/faster-whisper-medium.en
            echo "✅ TTS/STT Services Ready."

             # Update .env to use externalapi for Hybrid Mode
             # We check if we haven't already added this block to avoid duplicates if run multiple times
            if ! grep -q "TTS_PROVIDER=externalapi" .env; then
                 echo "" >> .env
                 echo "# Hybrid Mode Audio" >> .env
                 echo "TTS_PROVIDER=externalapi" >> .env
                 echo "TTS_BASE_URL=http://localhost:8969/v1" >> .env
                 echo "STT_PROVIDER=externalapi" >> .env
                 echo "STT_BASE_URL=http://localhost:8969/v1" >> .env
            fi

        else
             echo "❌ Docker not found. Skipping TTS start."
        fi
    fi
fi

echo ""
echo "✅ Setup Complete!"
echo "To run the application:"
echo "  conda activate Personal-Guru"
echo "  python run.py"
