from dotenv import load_dotenv
load_dotenv(override=True)
import os  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402

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

    app.run(
        debug=True,
        host='0.0.0.0',
        port=port,
        use_reloader=True,
        reloader_type='stat',
        exclude_patterns=[f'{sandbox_path}/*'],
        ssl_context=ssl_context
    )
