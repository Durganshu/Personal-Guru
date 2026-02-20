from flask import Flask, render_template, request
import os
import sys
import secrets


from flask_wtf.csrf import CSRFProtect

def create_setup_app():
    """
    Create a minimal Flask app for initial environment setup.

    Returns:
        Flask application with setup wizard routes.
    """
    app = Flask(__name__, template_folder='core/templates')
    app.secret_key = os.urandom(24) # Required for CSRF
    CSRFProtect(app)

    # Determine base directory (next to exe in frozen mode, project root in dev)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load defaults
    defaults = {}

    # Try loading from .env first, then .env.example (using absolute paths)
    env_file = os.path.join(base_dir, '.env')
    env_example = os.path.join(base_dir, '.env.example')
    env_path = env_file if os.path.exists(env_file) else env_example

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    defaults[key] = value

    @app.route('/', methods=['GET', 'POST'])
    def setup():
        """
        Handle the setup wizard logic.

        GET: Renders the setup form with current defaults.
        POST:
            - Validates input.
            - Writes configuration to .env file.
            - Triggers application restart by touching run.py.
            - Returns a client-side polling page to redirect the user once the server restarts.
        """
        if request.method == 'POST':
            # Gather form data
            config = {
                'DATABASE_URL': request.form.get('database_url'),
                'PORT': request.form.get('port', '5011'),
                'LLM_BASE_URL': request.form.get('LLM_BASE_URL'),
                'LLM_MODEL_NAME': request.form.get('llm_model'),
                'LLM_API_KEY': request.form.get('llm_key', ''),
                'LLM_MAX_OUTPUT_TOKENS': request.form.get('llm_ctx', '20000'),
                'TTS_BASE_URL': request.form.get('tts_url', ''),
                'OPENAI_API_KEY': request.form.get('openai_key', ''),
                'YOUTUBE_API_KEY': request.form.get('youtube_key', ''),
                'SECRET_KEY': os.environ.get('SECRET_KEY') or secrets.token_hex(32)
            }

            # Simple validation
            if not config['DATABASE_URL'] or not config['LLM_BASE_URL']:
                return "Missing required fields", 400

            # --- Convert relative SQLite paths to absolute paths in data folder ---
            db_url = config['DATABASE_URL']
            if db_url.startswith('sqlite:///') and not db_url.startswith('sqlite:////'):
                # Extract the filename (e.g., 'site.db' from 'sqlite:///site.db')
                db_filename = db_url.replace('sqlite:///', '')
                # If it's not an absolute path, make it absolute in the data folder
                if not os.path.isabs(db_filename):
                    data_dir = os.path.join(os.path.dirname(env_file), 'data')
                    os.makedirs(data_dir, exist_ok=True)
                    db_path = os.path.join(data_dir, db_filename).replace('\\', '/')
                    config['DATABASE_URL'] = f"sqlite:///{db_path}"
                    print(f"--- SETUP: Converted SQLite path to: {config['DATABASE_URL']}")

            # --- Capture Audio Settings ---
            # Default: TTS=externalapi, STT=native (for both frozen and dev, as per recent changes)
            default_tts_provider = 'externalapi'
            default_stt_provider = 'native'

            config.update({
                'TTS_PROVIDER': request.form.get('tts_provider', default_tts_provider),
                'TTS_BASE_URL': request.form.get('tts_url', ''),
                'TTS_MODEL': request.form.get('tts_model', 'tts-1'),
                'TTS_LANGUAGE': request.form.get('tts_language', 'en'),
                'TTS_VOICE_DEFAULT': request.form.get('tts_voice_default', 'af_heart'),
                'TTS_VOICE_PODCAST_HOST': request.form.get('tts_voice_host', 'af_heart'),
                'TTS_VOICE_PODCAST_GUEST': request.form.get('tts_voice_guest', 'am_michael'),
                'STT_PROVIDER': request.form.get('stt_provider', default_stt_provider),
                'STT_BASE_URL': request.form.get('stt_url', ''),
                'STT_MODEL': request.form.get('stt_model', 'Systran/faster-whisper-medium.en')
            })

            # Write to .env (use absolute path)
            with open(env_file, 'w') as f:
                for key, value in config.items():
                    f.write(f"{key}={value}\n")

            # --- Trigger Model Downloads if Native (Local) ---
            try:
                if config['STT_PROVIDER'] == 'native':
                    print("--- SETUP: Triggering Native STT Model Download (Whisper) ---")
                    try:
                        from app.common.audio_service import WhisperSTT
                        WhisperSTT()
                        print("--- SETUP: STT Models Ready ---")
                    except Exception as e:
                        print(f"--- SETUP WARNING: Failed to download STT models: {e}")

                # --- Initialize Shared Sandbox ---
                # We skip this in setup because it can be slow/blocking.
                # It will be handled on next startup by run.py or entry_point.py
                print("--- SETUP: Sandbox initialization deferred to next startup ---")

            except Exception as e:
                print(f"--- SETUP: Error during model pre-load: {e}")


            # Trigger restart based on environment
            is_frozen = getattr(sys, 'frozen', False)

            if is_frozen:
                # In frozen mode, we can't touch run.py - show manual restart message
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Configuration Saved</title>
                    <style>
                        body { font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #f0f2f5; margin: 0; }
                        .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; max-width: 450px; }
                        h2 { color: #059669; margin-top: 0; }
                        p { color: #4b5563; line-height: 1.6; }
                        .icon { font-size: 3rem; margin-bottom: 1rem; }
                        .btn { display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: #059669; color: white; text-decoration: none; border-radius: 8px; font-weight: 500; }
                        .btn:hover { background: #047857; }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <div class="icon">✅</div>
                        <h2>Configuration Saved!</h2>
                        <p>Your settings have been saved successfully.</p>
                        <p><strong>Please close this application and restart it</strong> to apply the new configuration.</p>
                        <p style="font-size:0.85rem; color:#6b7280;">The application will now use your new settings on the next launch.</p>
                    </div>
                </body>
                </html>
                """
            else:
                # Development mode - touch run.py to trigger Flask reload
                try:
                    os.utime('run.py', None)
                except Exception as e:
                    print(f"Error triggering reload: {e}")

                # Return a page that polls for the server to come back up
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Restarting...</title>
                    <style>
                        body { font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #f0f2f5; margin: 0; }
                        .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
                        h2 { color: #059669; margin-top: 0; }
                        p { color: #4b5563; }
                        .loader { border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; margin: 1rem auto; }
                        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h2>Configuration Saved!</h2>
                        <div class="loader"></div>
                        <p>Restarting server and applying changes...</p>
                        <p style="font-size:0.9rem">You will be redirected automatically.</p>
                    </div>
                    <script>
                        // Poll the server every 2 seconds to see if it's back up
                        const checkServer = async () => {
                            try {
                                const controller = new AbortController();
                                const timeoutId = setTimeout(() => controller.abort(), 2000);

                                // Try to fetch home page
                                const response = await fetch('/', {
                                    method: 'HEAD',
                                    signal: controller.signal,
                                    cache: 'no-store'
                                });

                                if (response.ok) {
                                    window.location.href = '/';
                                }
                            } catch (e) {
                                // Server still restarting, ignore error
                                console.log('Waiting for server...');
                            }
                        };

                        // Give it a moment to actually die first
                        setTimeout(() => {
                            setInterval(checkServer, 2000);
                        }, 3000);
                    </script>
                </body>
                </html>
                """

        return render_template('setup.html', defaults=defaults, is_frozen=getattr(sys, 'frozen', False))

    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    return app
