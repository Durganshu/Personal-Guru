# Setup Guide: Power Users

This guide is for users who want to run the full stack using Docker and configure external APIs (LLM, TTS, STT) for maximum performance and flexibility.

## Full Docker Setup (Recommended for Servers)

This method runs the entire application stack (App, Database, TTS services) in isolated Docker containers using the provided helper scripts.

### Prerequisites

* **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (or docker engine/plugin) installed.
* **[Git](https://git-scm.com/downloads)** installed.

### Installation Steps

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/Rishabh-Bajpai/Personal-Guru.git
    cd Personal-Guru
    ```

2. **Configure Environment (Optional)**:
    Generally, the default configuration works out of the box. However, if you want to customize settings (e.g., use an external LLM like LMStudio running on another machine), you can create a `.env` file.

    ```bash
    cp .env.example .env
    # Edit the file with your preferred editor
    nano .env
    ```

3. **Run with Docker**:
    Use the provided script to start the containers. It handles profile selection (e.g., enabling TTS) and detached mode.
    * **Linux/Mac**:

        ```bash
        ./scripts/installation/start_docker.sh
        ```

    * **Windows**:

        ```cmd
        scripts\installation\start_docker.bat
        ```

    * **Access the app at**: `http://localhost:5011`

4. **Stop Docker**:
    To correctly stop all services:
    * **Linux/Mac**:

        ```bash
        ./scripts/installation/stop_docker.sh
        ```

    * **Windows**:

        ```cmd
        scripts\installation\stop_docker.bat
        ```

---

## Configuring External APIs

Personal Guru allows you to offload processing to external providers.

### Supported Providers

* **LLM**: Ollama (native), OpenAI, Anthropic, Gemini, etc.
* **TTS**: Kokoro (local), OpenAI (via API).
* **STT**: Whisper (local), OpenAI (via API).

*Note: Currently, only Kokoro and Whisper are fully integrated as managed services within the Docker stack. Other providers require manual configuration of the Base URL and API Key.*

### Configuration

Edit your `.env` file to set the variables, or proceed with the default variables and edit later using the GUI


#### Custom LLM Base URL (e.g., Remote Ollama)

```ini
LLM_BASE_URL=http://your-ollama-server:11434/v1
LLM_MODEL_NAME=llama3
```

After changing `.env`, restart the Docker containers using the start script or:

```bash
docker compose up -d --force-recreate
```
