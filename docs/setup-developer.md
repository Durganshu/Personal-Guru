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
    flask db migrate -m "Description"
    flask db upgrade
    ```
