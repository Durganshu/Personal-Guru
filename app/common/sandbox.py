import os
import sys
import subprocess
import venv
import shutil
import uuid
import glob
import logging
import threading
import base64
import hashlib
import time
import stat
from config import Config

logger = logging.getLogger(__name__)

def force_rmtree(path):
    """
    Robustly removes a directory, handling platform-specific issues like file locks and readonly attributes.
    """
    if not os.path.exists(path):
        return

    def on_error(func, path, exc_info):
        """Error handler for shutil.rmtree to handle readonly files."""
        # Check if it's a 'permission denied' error
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        else:
            raise

    # Try up to 3 times with a small delay for OS file locks to clear
    for i in range(3):
        try:
            shutil.rmtree(path, onerror=on_error)
            return
        except Exception as e:
            if i < 2:
                logger.warning(f"rmtree failed for {path}, retrying... ({e})")
                time.sleep(1)
            else:
                logger.error(f"Final rmtree attempt failed for {path}: {e}")
                # Fallback: rename the folder to "marked_for_deletion" so it doesn't block recreation
                try:
                    trash_path = path + f"_old_{int(time.time())}"
                    os.rename(path, trash_path)
                    logger.info(f"Renamed stuck folder to {trash_path}")
                except Exception as rename_e:
                    logger.error(f"Even rename failed: {rename_e}")

SHARED_SANDBOX_ID = "shared_env"
# Libraries that should be pre-installed in the shared sandbox
PREINSTALLED_LIBS = ['numpy', 'pandas', 'matplotlib', 'scipy', 'seaborn']

def _validate_python_executable(path):
    """Checks if a given path points to a working Python interpreter."""
    if not path or not os.path.isabs(path) or not os.path.isfile(path):
        return False
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False

def get_system_python():
    """
    Finds a suitable system Python executable.
    Crucial for frozen app (PyInstaller) where sys.executable is the binary.
    Returns an absolute path to a validated Python executable, or None.
    """
    # If not frozen, use current interpreter
    if not getattr(sys, 'frozen', False):
        return sys.executable

    # In frozen mode, search for system python
    candidates = []

    # 1. Check PATH
    path_python = shutil.which('python')
    if path_python and 'windowsapps' not in path_python.lower():
        candidates.append(os.path.abspath(path_python))

    # 2. Common Windows Paths
    if os.name == 'nt':
        candidates.extend([
            r"C:\Python311\python.exe",
            r"C:\Python312\python.exe",
            r"C:\Python310\python.exe",
            r"C:\Python39\python.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python311\python.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python312\python.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python310\python.exe"),
        ])

    # Validate each candidate
    for candidate in candidates:
        if _validate_python_executable(candidate):
            logger.info(f"Found valid system Python: {candidate}")
            return candidate

    logger.warning("No valid system Python found.")
    return None

def is_sandbox_available():
    """Checks if a valid Python interpreter is available for creating sandboxes."""
    return get_system_python() is not None

def get_sandbox_id(user_id, topic_name):
    """Generates a deterministic sandbox ID for a user and topic."""
    # Hash the entire combo to keep paths ultra-short to ensure compatibility with all OS path limits
    combined = f"{user_id}_{topic_name}"
    short_hash = hashlib.md5(combined.encode()).hexdigest()[:16]
    return f"sb_{short_hash}"

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
    if not is_sandbox_available():
        logger.warning("No system Python found. Sandbox creation skipped.")
        return

    logger.info(f"Checking shared sandbox: {SHARED_SANDBOX_ID}")

    # We use the Sandbox class to handle creation
    sb = Sandbox(sandbox_id=SHARED_SANDBOX_ID)
    ready_file = os.path.join(sb.path, ".ready")

    # If it's already ready, just skip
    if os.path.exists(ready_file):
        logger.info("Shared sandbox is already marked as READY.")
        return

    # Check if libraries are actually usable
    check_script = "import numpy; import pandas; import matplotlib; print('Libs OK')"
    result = sb.run_code(check_script)

    if "Libs OK" not in result.get('output', ''):
        logger.info(f"Shared sandbox missing libraries. Installing: {PREINSTALLED_LIBS}")
        try:
            sb.install_deps(PREINSTALLED_LIBS)
            # Create the sentinel file when truly done
            with open(ready_file, "w") as f:
                f.write("ready")
            logger.info("Shared sandbox libraries installed and marked as READY.")
        except Exception as e:
            logger.error(f"Failed to install shared libs: {e}")
    else:
        # If it was already OK but missing the file for some reason, create it
        with open(ready_file, "w") as f:
            f.write("ready")
        logger.info("Shared sandbox libraries verified and marked as READY.")

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
            force_rmtree(path)
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

        # Set paths for the local venv (might not exist yet)
        if os.name == 'nt':
            self.local_python = os.path.join(self.venv_path, "Scripts", "python.exe")
        else:
            self.local_python = os.path.join(self.venv_path, "bin", "python")

    @property
    def python_executable(self):
        """Returns the best available python executable (local or shared fallback)."""
        if os.path.exists(self.local_python):
            return self.local_python

        # Fallback to template if we haven't created a local venv yet
        if self.template_id:
            template_path = os.path.join(self.base_path, self.template_id, "venv")
            if os.name == 'nt':
                fallback = os.path.join(template_path, "Scripts", "python.exe")
            else:
                fallback = os.path.join(template_path, "bin", "python")

            if os.path.exists(fallback):
                return fallback

        return get_system_python()

    def _create_venv(self):
        """Creates the environment, optionally cloning from template."""

        # Cloning Logic
        if self.template_id:
            template_path = os.path.join(self.base_path, self.template_id, "venv")
            if os.path.exists(template_path):
                # Wait for .ready file if cloning from shared_env
                if self.template_id == SHARED_SANDBOX_ID:
                    ready_file = os.path.join(os.path.dirname(template_path), ".ready")
                    import time
                    attempts = 0
                    while not os.path.exists(ready_file) and attempts < 10:
                        logger.info(f"Waiting for shared sandbox to be READY (attempt {attempts+1})...")
                        time.sleep(5)
                        attempts += 1

                logger.info(f"Cloning sandbox {self.id} from template {self.template_id}...")
                try:
                    # 1. Clear target if it exists (partial failed clone)
                    if os.path.exists(self.venv_path):
                        force_rmtree(self.venv_path)

                    # 2. Copy the venv directory
                    shutil.copytree(template_path, self.venv_path, symlinks=True)

                    # 3. Fix the venv scripts by running venv update on top
                    builder = venv.EnvBuilder(with_pip=True, clear=False)
                    builder.create(self.venv_path)

                    logger.info(f"Sandbox {self.id} cloned successfully.")
                    return
                except Exception as e:
                    logger.error(f"Clone failed: {e}. Falling back to fresh install.")
                    if os.path.exists(self.venv_path):
                         force_rmtree(self.venv_path)
            else:
                logger.warning(f"Template {self.template_id} not found. Creating fresh.")

        # Fresh Creation Logic
        logger.info(f"Creating new sandbox environment: {self.id}")

        # Ensure base path exists
        os.makedirs(self.path, exist_ok=True)

        system_python = get_system_python()
        if not system_python:
             logger.error("FATAL: No valid system Python found. Cannot create sandbox.")
             return

        try:
             # In frozen mode, we MUST run venv as a subprocess using the found system python
             if getattr(sys, 'frozen', False):
                 logger.info(f"Frozen mode detected. Creating venv using {system_python}")
                 subprocess.check_call(
                     [system_python, "-m", "venv", "--system-site-packages", self.venv_path],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL
                 )
             else:
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

        # Ensure local venv exists before installing
        if not os.path.exists(self.local_python):
            logger.info(f"Local venv missing for {self.id}. Creating/Cloning now for dependencies...")
            self._create_venv()

        try:
            # Use python -m pip for cross-platform reliability
            # Capture output so we can log it on failure
            subprocess.run(
                [self.python_executable, "-m", "pip", "install"] + dependencies,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Dependencies installed.")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or str(e)
            logger.error(f"Failed to install dependencies: {error_msg}")
            # Raise a clear error that will be caught by the route handler
            raise Exception(f"Dependency installation failed: {error_msg}")

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
        setup_code = """# -*- coding: utf-8 -*-
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

        # Auto-display wrapper for simple assignments (Jupyter-style behavior)
        # Detect if code has simple assignments but no print/output statements
        import re
        has_assignment = bool(re.search(r'^\s*\w+\s*=\s*.+$', code, re.MULTILINE))
        has_output = 'print(' in code or 'plt.' in code or 'display(' in code

        auto_display_code = ""
        if has_assignment and not has_output:
            # Extract variable names from assignments
            var_names = re.findall(r'^\s*(\w+)\s*=', code, re.MULTILINE)
            if var_names:
                auto_display_code = "\n# Auto-display variables\n"
                for var in var_names:
                    auto_display_code += f"print(f'{var} = {{{var}}}')\n"

        full_code = setup_code + "\n" + code + auto_display_code

        with open(script_path, "w", encoding='utf-8') as f:
            f.write(full_code)

        python_path = self.python_executable

        images = []
        try:
            logger.info(f"Executing script in {self.id}")
            logger.info(f"Python Executable: {python_path}")
            logger.info(f"CWD: {self.path}")

            if not os.path.exists(python_path):
                logger.error(f"FATAL: Python executable not found at {python_path}")
                # List the Scripts/bin dir to see what's there
                script_dir = os.path.dirname(python_path)
                if os.path.exists(script_dir):
                     logger.info(f"Contents of {script_dir}: {os.listdir(script_dir)}")
                else:
                     logger.error(f"Script directory {script_dir} does not exist!")

                # Return error instead of crashing
                return {
                    "output": "",
                    "error": "Python is not installed on this system. Code execution is disabled.",
                    "images": []
                }

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
            force_rmtree(self.path)
