# Setup Guide: Normal Users

This guide is designed for users who want the easiest way to run **Personal Guru** on their local machine without complex configuration.

## Option 1: Using the Executable (Recommended for Windows)

The easiest way to run Personal Guru on Windows is by using the standalone `.exe` file. This "Frozen Mode" includes everything you need.

### Steps

1. **Download** the latest `PersonalGuru.exe` from the [Releases page](https://github.com/Rishabh-Bajpai/Personal-Guru/releases).
2. **Move** the file to a dedicated folder (e.g., `C:\PersonalGuru`).
3. **Run** `PersonalGuru.exe`.
    * *Note: On the first run, it will extract necessary files and set up a local database (`site.db`) in the same folder. The app may take a few minutes to start on the first run.*
4. Open your browser and navigate to `http://localhost:5011`.

**Pros:** No installation required, portable.
**Cons:** Windows only, limited customization, and slow on windows and low end devices.

---

## Option 2: Local Lite Mode (Non-Docker)

If you are on Linux/Mac, or prefer running from source without Docker, use the **Local Lite Mode**. This uses a local SQLite database and runs everything directly on your machine.

### Prerequisites

* **[Miniconda](https://docs.conda.io/en/latest/miniconda.html)** or **[Anaconda](https://www.anaconda.com/download)** installed.
* **[Git](https://git-scm.com/downloads)** installed.
* **[FFmpeg](https://ffmpeg.org/download.html)** installed (Required for audio processing).

### Installation Steps

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/Rishabh-Bajpai/Personal-Guru.git
    cd Personal-Guru
    ```

2. **Run the Setup Script**:
    * **Linux/Mac**:

        ```bash
        ./scripts/installation/setup.sh
        ```

    * **Windows**:

        ```cmd
        scripts\installation\setup.bat
        ```

3. **Select "Local Lite Mode"**:
    * When prompted, choose option **`2`** ("Local Lite Mode").
    * This will set up a local environment using SQLite and disable Docker requirements.

4. **Run the Application**:

    ```bash
    conda activate Personal-Guru
    python run.py
    ```

5. Access the app at `http://localhost:5011`.
