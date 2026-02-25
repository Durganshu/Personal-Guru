# AI Book Cover Generation Setup

Personal-Guru uses **ComfyUI** to generate custom AI book covers for newly generated studying materials via websockets. This feature is completely **optional**—if you do not set it up or the files are missing, the system will gracefully skip the generation and default to standard book covers.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Workflow Configuration](#workflow-configuration)
4. [Testing the Setup](#testing-the-setup)

## Prerequisites

To enable AI book cover generation, you must have the following dependencies:

1. A running instance of **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** (either running locally or inside a Docker container).
2. The `websocket-client` Python library installed in your environment:
   ```bash
   pip install websocket-client
   ```

## Environment Configuration

In your `.env` (or `.env.local` / `.env.example`) file, you need to configure the connection to your ComfyUI server and specify where your workflow API JSON is located.

```env
# =============================================================================
# COMFYUI (Book Cover Generation)
# =============================================================================
# ComfyUI server address for AI book cover generation
# If running locally: localhost:8188
# If running in Docker: host.docker.internal:8188
COMFYUI_SERVER_ADDRESS=localhost:8188

# Path to the ComfyUI workflow JSON file (defaults to scripts/example_workflow.json)
COMFYUI_WORKFLOW_PATH=scripts/example_workflow.json
```

## Workflow Configuration

ComfyUI operates using graphical "workflows" that can be saved into JSON formatting.
To instruct Personal-Guru on what kind of book covers to generate:

1. You must provide a valid ComfyUI workflow JSON file at the path specified by `COMFYUI_WORKFLOW_PATH`. We provide `scripts/example_workflow.json` as a default.
2. The backend integration (`app/modes/library/book_cover.py`) replaces specific nodes dynamically containing standard ComfyUI widgets (such as `CLIPTextEncode` for positive prompt, and aspects of `EmptySD3LatentImage`, `KSampler`, etc.).
3. **Important:** The provided JSON must be in **API Format**. To export an API Format JSON from ComfyUI, you must enable "Enable Dev mode Options" in the ComfyUI settings (gear icon), then click the "Save (API Format)" button.

## Testing the Setup

You can manually test your ComfyUI book cover generation setup without spinning up the entire frontend by using the included example script:

```bash
# Ensure your environment is active (e.g. `conda activate Personal-Guru`)
python scripts/examples/generate_book_cover.py
```

This will connect to your ComfyUI server, queue a generation job using `scripts/example_workflow.json`, wait for completion, and save the resulting PNG locally in your current directory.
