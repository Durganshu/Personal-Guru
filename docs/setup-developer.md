# Setup Guide: Developers

This guide is for contributors and developers who need a robust environment for modifying the code. It uses **Hybrid Mode**: Docker for heavy backend services (DB, TTS) and the local terminal for the Flask application to enable features like auto-reloading and debugging.

## Hybrid Mode Setup

In this mode, you run the support services in Docker but the main app locally.

### Prerequisites

* **Conda** (Miniconda/Anaconda).
* **Docker** and **Docker Compose**.
* **Git**.

### Installation Steps

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/Rishabh-Bajpai/Personal-Guru.git
    cd Personal-Guru
    git checkout development
    ```

    *Note: Active development happens on the `development` branch.*

2. **Run the Setup Script**:
    * **Linux/Mac**: `./scripts/installation/setup.sh`
    * **Windows**: `scripts\installation\setup.bat`

3. **Select "Hybrid Mode"**:
    * Choose option **`1`** ("Hybrid Mode").
    * The script will install **development dependencies** (`.[dev]`) and setup `pre-commit` hooks.
    * It will ask if you want to start the Docker Database. Say **Yes**.

4. **Activate Environment**:

    ```bash
    conda activate Personal-Guru
    ```

5. **Start Services (If not already running)**:
    If you didn't start the DB during setup, or need to restart it:
    * **Linux/Mac**: `./scripts/installation/start_docker.sh`
    * **Windows**: `scripts\installation\start_docker.bat`

    *Select option `Yes` if you want to run local Speaches (TTS/STT).*

6. **Run the Application**:

    ```bash
    python run.py
    ```

    * The app will connect to the localhost ports exposed by Docker (DB: 5433, TTS: 8969).

---

## Developer Workflow

### Running Tests

To run the full test suite:

```bash
python -m pytest
```

### Database Management

* **View DB**: `python scripts/db_viewer.py`
* **Clear DB**: `python scripts/clear_database.py` (Caution!)
* **Migrations**:

    ```bash
    flask db upgrade
    ```

## Utility Scripts for Developers

The `scripts/` folder contains several utility scripts to assist with development, database management, and visualization.

### Database Tools

- **`scripts/generate_dbml.py`**
  - **Purpose:** Generates a DBML (Database Markup Language) file from your SQLAlchemy models.
  - **Usage:** `python scripts/generate_dbml.py > schema.dbml`
  - **Use Case:** Copy the output to [dbdiagram.io](https://dbdiagram.io) to visualize and interactively edit your schema.

- **`scripts/visualize_db.py`**
  - **Purpose:** Generates a Mermaid.js Entity Relationship Diagram (ERD).
  - **Usage:** `python scripts/visualize_db.py`
  - **Use Case:** Copy the output into a Markdown file (like `docs/schema.md`) to view the diagram directly in GitHub or compatible editors.

- **`scripts/db_viewer.py`**
  - **Purpose:** Launches a visual web interface (Flask-Admin) to browse and manage database records.
  - **Usage:** `python scripts/db_viewer.py`
  - **URL:** Open `http://localhost:5012` to view tables.

- **`scripts/update_database.py`**
  - **Purpose:** Initializes tables and performs safe migrations (adding new columns/tables).
  - **Usage:** `python scripts/update_database.py`

### Other Utilities

- **`scripts/generate_cert.py`**
  - **Purpose:** Generates self-signed SSL certificates (`cert.pem`, `key.pem`) for local HTTPS development (required for microphone access).
  - **Usage:** `python scripts/generate_cert.py`

## Pre-commit Hooks

This project uses `pre-commit` to ensure code quality (linting, formatting, checking for merge conflicts, etc.) before every commit.

### Installation

1. **Install the hooks:**

    ```bash
    pre-commit install
    ```

2. **Run manually (optional):**
    To run the hooks on all files without committing:

    ```bash
    pre-commit run --all-files
    ```

### Hooks Included

- **Trailing Whitespace**: Removes trailing whitespace.
- **Merge Conflicts**: Checks for unresolved merge conflict markers.
- **Black**: Formats Python code.
- **Ruff**: Lints Python code.
- **Codespell**: Checks for spelling errors.
- **Interrogate**: Checks for missing docstrings in Python code.
