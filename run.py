from dotenv import load_dotenv
import os
import logging
import sys

# --- Robust Environment Loading for Docker/Windows ---
# 1. Capture critical variables injected by Docker (which are correct for internal networking)
# 1. Capture critical variables injected by Docker (which are correct for internal networking)
docker_db_url = os.environ.get('DATABASE_URL')
docker_tts_url = os.environ.get('TTS_BASE_URL')
docker_stt_url = os.environ.get('STT_BASE_URL')
docker_tts_provider = os.environ.get('TTS_PROVIDER')
docker_stt_provider = os.environ.get('STT_PROVIDER')

# 2. Force-load .env to get the latest user configuration (overriding stale Docker vars)
load_dotenv(override=True)

# 3. Restore critical Docker variables if they were valid internal services
# This prevents local .env values (like sqlite:/// or localhost) from breaking the container.
if docker_db_url and 'postgres' in docker_db_url:
    os.environ['DATABASE_URL'] = docker_db_url

if docker_tts_url and 'speaches' in docker_tts_url:
    os.environ['TTS_BASE_URL'] = docker_tts_url

if docker_stt_url and 'speaches' in docker_stt_url:
    os.environ['STT_BASE_URL'] = docker_stt_url

# Restore providers if they were set (usually 'externalapi' in Docker)
if docker_tts_provider == 'externalapi':
    os.environ['TTS_PROVIDER'] = docker_tts_provider

if docker_stt_provider == 'externalapi':
    os.environ['STT_PROVIDER'] = docker_stt_provider

print("----------------------------------------------------------------")
print(f"🚀 Starting App with LLM_MODEL_NAME: {os.environ.get('LLM_MODEL_NAME', 'Not Set')}")
print("----------------------------------------------------------------")

# Configure logging at the entry point to ensure visibility of startup tasks
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from app.common.config_validator import validate_config  # noqa: E402


# Check configuration
missing_vars = validate_config()

if missing_vars:
    print(f"Missing configuration variables: {missing_vars}. Starting Setup Wizard...")
    from app.setup_app import create_setup_app
    app = create_setup_app()
else:
    from app import create_app  # noqa: E402
    from app.common.sandbox import ensure_shared_sandbox
    # Ensure shared sandbox is ready
    ensure_shared_sandbox()
    app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5011))
    # Exclude sandbox directory from reloader monitoring to prevent restart loops
    # when creating temporary environments
    sandbox_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'sandbox')
    cert_path = os.path.join('certs', 'cert.pem')
    key_path = os.path.join('certs', 'key.pem')

    ssl_context = None
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"SSL Certificates found. Enabling HTTPS on port {port}.")
        ssl_context = (cert_path, key_path)
    else:
        print(f"No SSL Certificates found. Running on HTTP port {port}.")

    # Ensure flask_session directory exists to prevent cachelib FileNotFoundError
    # Docker containers often mount volumes where this directory doesn't exist initially.
    session_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    try:
        os.makedirs(session_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create session directory {session_dir}: {e}")

    app.run(
        debug=True,
        host='0.0.0.0',
        port=port,
        use_reloader=True,
        reloader_type='stat',
        exclude_patterns=[f'{sandbox_path}/*'],
        ssl_context=ssl_context
    )
