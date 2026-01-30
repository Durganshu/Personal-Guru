import os
import subprocess
import venv
import shutil
import uuid
import glob
import logging
import threading
import base64
from config import Config

logger = logging.getLogger(__name__)

SHARED_SANDBOX_ID = "shared_env"
# Libraries that should be pre-installed in the shared sandbox
PREINSTALLED_LIBS = ['numpy', 'pandas', 'matplotlib', 'scipy', 'seaborn']

def get_sandbox_id(user_id, topic_name):
    """Generates a deterministic sandbox ID for a user and topic."""
    # Sanitize topic name: keep alphanumeric, replace others with underscore
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic_name])
    return f"user_{user_id}_{safe_topic}"

def cleanup_old_sandboxes(base_path=None):
    """Deprecated: Use _cleanup_user_sandboxes instead. Kept for backward compatibility with install scripts."""
    # We can effectively do nothing here, or just basic cleanup of non-shared if absolutely needed.
    # But since the new logic handles cleanup per-user, we can just log a warning.
    logger.warning("cleanup_old_sandboxes is deprecated. Cleanup is now handled per-topic.")

def ensure_shared_sandbox():
    """
    Ensures the shared sandbox exists and has essential libraries installed.
    Should be called on application startup.
    """
    logger.info(f"Checking shared sandbox: {SHARED_SANDBOX_ID}")

    # We use the Sandbox class to handle creation
    sb = Sandbox(sandbox_id=SHARED_SANDBOX_ID)

    # Check if libraries are actually usable (simple import check)
    check_script = "import numpy; import pandas; import matplotlib; print('Libs OK')"
    result = sb.run_code(check_script)

    if "Libs OK" not in result.get('output', ''):
        logger.info(f"Shared sandbox missing libraries. Installing: {PREINSTALLED_LIBS}")
        try:
            sb.install_deps(PREINSTALLED_LIBS)
            logger.info("Shared sandbox libraries installed successfully.")
        except Exception as e:
            logger.error(f"Failed to install shared libs: {e}")
    else:
        logger.info("Shared sandbox libraries verified.")

def background_init_topic_sandbox(user_id, topic_name):
    """
    Starts a background thread to initialize the topic sandbox.
    It clones the shared sandbox to ensure immediate availability of libraries.
    """
    def _init_task():
        target_id = get_sandbox_id(user_id, topic_name)
        logger.info(f"Background: Initializing sandbox {target_id} from shared...")

        # 1. Cleanup other sandboxes for this user
        _cleanup_user_sandboxes(user_id, target_id)

        # 2. Trigger creation (Sandbox init logic handles cloning if template provided)
        try:
             # Instantiating with template_id triggers the clone if directory is missing
             Sandbox(sandbox_id=target_id, template_id=SHARED_SANDBOX_ID)
             logger.info(f"Background: Sandbox {target_id} ready.")
        except Exception as e:
             logger.error(f"Background: Failed to init sandbox {target_id}: {e}")

    thread = threading.Thread(target=_init_task)
    thread.daemon = True
    thread.start()

def _cleanup_user_sandboxes(user_id, active_sandbox_id):
    """
    Removes sandboxes belonging to the user that are NOT the active one.
    This ensures we don't accumulate junk while switching topics.
    """
    base_path = Config.SANDBOX_PATH
    if not os.path.exists(base_path):
        return

    # Glob pattern for this user's sandboxes
    pattern = os.path.join(base_path, f"user_{user_id}_*")

    for path in glob.glob(pattern):
        folder_name = os.path.basename(path)

        # Skip the active one (and strictly skip shared_env, though pattern shouldn't match it)
        if folder_name == active_sandbox_id or folder_name == SHARED_SANDBOX_ID:
            continue

        try:
            logger.info(f"Cleaning up inactive sandbox: {folder_name}")
            shutil.rmtree(path)
        except Exception as e:
            logger.warning(f"Failed to remove sandbox {folder_name}: {e}")


class Sandbox:
    """Isolated Python execution environment with cloning capabilities."""

    def __init__(self, base_path=None, sandbox_id=None, template_id=None):
        """
        Initialize the sandbox environment.

        Args:
            base_path: Root directory for sandboxes (default: data/sandbox)
            sandbox_id: Unique ID for this sandbox.
            template_id: ID of an existing sandbox to clone from if creating new.
        """
        if base_path:
            self.base_path = base_path
        else:
            self.base_path = Config.SANDBOX_PATH

        self.id = sandbox_id if sandbox_id else str(uuid.uuid4())
        self.path = os.path.join(self.base_path, self.id)
        self.venv_path = os.path.join(self.path, "venv")
        self.template_id = template_id

        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        # Create/Resurrect/Clone venv if not exists
        if not os.path.exists(self.venv_path):
            self._create_venv()

        # Set paths
        if os.name == 'nt':
            self.python_executable = os.path.join(self.venv_path, "Scripts", "python.exe")
        else:
            self.python_executable = os.path.join(self.venv_path, "bin", "python")

    def _create_venv(self):
        """Creates the environment, optionally cloning from template."""

        # Cloning Logic
        if self.template_id:
            template_path = os.path.join(self.base_path, self.template_id, "venv")
            if os.path.exists(template_path):
                logger.info(f"Cloning sandbox {self.id} from template {self.template_id}...")
                try:
                    # 1. Copy the venv directory
                    shutil.copytree(template_path, self.venv_path, symlinks=True)

                    # 2. Fix the venv scripts by running venv update on top
                    builder = venv.EnvBuilder(with_pip=True, clear=False)
                    builder.create(self.venv_path)

                    logger.info(f"Sandbox {self.id} cloned successfully.")
                    return
                except Exception as e:
                    logger.error(f"Clone failed: {e}. Falling back to fresh install.")
                    if os.path.exists(self.venv_path):
                         shutil.rmtree(self.venv_path)
            else:
                logger.warning(f"Template {self.template_id} not found. Creating fresh.")

        # Fresh Creation Logic
        logger.info(f"Creating new sandbox environment: {self.id}")

        # Ensure base path exists
        os.makedirs(self.path, exist_ok=True)

        try:
             builder = venv.EnvBuilder(with_pip=True)
             builder.create(self.venv_path)
             logger.info("Virtual environment created.")
        except Exception as e:
             logger.error(f"Failed to create venv: {e}")

    def install_deps(self, dependencies):
        """Installs dependencies in the sandbox."""
        if not dependencies:
            return

        logger.info(f"Installing dependencies in {self.id}: {dependencies}")

        if os.name == 'nt':
            pip_path = os.path.join(self.venv_path, "Scripts", "pip")
        else:
            pip_path = os.path.join(self.venv_path, "bin", "pip")

        try:
            # Install
            subprocess.check_call(
                [pip_path, "install"] + dependencies,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info("Dependencies installed.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            raise

    def run_code(self, code):
        """Runs the provided code in the sandbox."""
        logger.info(f"Sandbox {self.id}: Preparing to run code...")

        # Clean up old images from previous runs to avoid showing stale plots
        for img_path in glob.glob(os.path.join(self.path, "*.png")):
            try:
                os.remove(img_path)
            except OSError:
                pass

        script_path = os.path.join(self.path, "script.py")

        # Custom matplotlib handler
        setup_code = """
import sys
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import uuid

    _original_show = plt.show

    def _custom_show(*args, **kwargs):
        is_interactive = False
        try:
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                for ax in fig.get_axes():
                    if getattr(ax, 'name', '') == '3d':
                        is_interactive = True
                        break
        except Exception:
            pass

        if is_interactive:
            print("Interactive plot detected. Opening window...")
            _original_show(*args, **kwargs)
        else:
            filename = f"plot_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(filename)
            plt.close()

    plt.show = _custom_show
except ImportError:
    pass
"""
        full_code = setup_code + "\n" + code

        with open(script_path, "w") as f:
            f.write(full_code)

        if os.name == 'nt':
            python_path = os.path.join(self.venv_path, "Scripts", "python")
        else:
            python_path = os.path.join(self.venv_path, "bin", "python")

        images = []
        try:
            logger.info(f"Executing script in {self.id}")
            result = subprocess.run(
                [python_path, "script.py"],
                cwd=self.path,
                capture_output=True,
                check=False,
                timeout=600
            )
            output = result.stdout.decode()
            error = result.stderr.decode()
            logger.info("Execution completed.")
        except subprocess.TimeoutExpired:
            output = ""
            error = "Execution timed out."
            logger.error("Execution timed out.")
        except Exception as e:
            output = ""
            error = str(e)
            logger.error(f"Execution failed: {e}")

        # Collect images
        for img_path in glob.glob(os.path.join(self.path, "*.png")):
            try:
                with open(img_path, "rb") as f:
                    encoded_img = base64.b64encode(f.read()).decode('utf-8')
                    images.append(encoded_img)
                os.remove(img_path)
            except Exception as e:
                logger.error(f"Failed to process image {img_path}: {e}")

        return {
            "output": output,
            "error": error,
            "images": images
        }

    def cleanup(self):
        """Removes the sandbox directory."""
        if os.path.exists(self.path):
            logger.info(f"Cleaning up sandbox: {self.path}")
            shutil.rmtree(self.path)
