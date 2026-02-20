# External Integrations

**Analysis Date:** 2025-02-15

## APIs & External Services

**Large Language Models (LLM):**
- OpenAI-compatible API - Primary reasoning engine (Ollama, LMStudio, or OpenAI).
  - SDK/Client: `openai` Python package.
  - Auth: `LLM_API_KEY` or `OPENAI_API_KEY`.
  - Base URL: `LLM_BASE_URL` (defaults to `http://localhost:11434/v1` in Docker).

**Text-to-Speech (TTS):**
- Speaches AI (Docker) or OpenAI API - Audio synthesis for study content and podcasts.
  - SDK/Client: `openai` Python package / custom `audio_service`.
  - Auth: `OPENAI_API_KEY` (if remote).
  - Base URL: `TTS_BASE_URL` (defaults to `http://localhost:8969/v1`).

**Speech-to-Text (STT):**
- Speaches AI (Docker) or Local `faster-whisper` - Audio transcription for user feedback.
  - SDK/Client: `openai` package (for Speaches/OpenAI) or `faster-whisper`.
  - Auth: `OPENAI_API_KEY` (if remote).
  - Base URL: `STT_BASE_URL`.

**Social Media Content:**
- YouTube Data API v3 - Searching and retrieving YouTube Reels/Shorts for specific topics.
  - SDK/Client: `google-api-python-client`.
  - Auth: `YOUTUBE_API_KEY`.
  - Frontend: `https://www.youtube.com/iframe_api`.

**Version Updates:**
- GitHub API - Checking for new releases of Personal-Guru.
  - Auth: None (public read).
  - Endpoint: `api.github.com/repos/Rishabh-Bajpai/Personal-Guru/releases/latest`.

## Data Storage

**Databases:**
- PostgreSQL 15 - Primary persistent storage for users, topics, learning modes, and logs.
  - Connection: `DATABASE_URL` (usually `postgresql://postgres:postgres@localhost:5433/personal_guru` in Docker).
  - Client: SQLAlchemy (ORM) and `psycopg2-binary`.
  - Support: `pgvector` for similarity search (commented in models but available in stack).

**File Storage:**
- Local Filesystem - Used for:
  - Audio files (`app/static/step_*.wav`).
  - Session data (`flask_session/`).
  - Database migrations (`migrations/`).
  - Sandbox data (`data/sandbox/`).

**Caching:**
- Filesystem-based sessions via `Flask-Session`.

## Authentication & Identity

**Auth Provider:**
- Custom identity management using `flask-login`.
  - Implementation: `Login` model with `password_hash` (PBKDF2).
  - Security: `Authlib` used for JWE (JSON Web Encryption) in `app/common/auth.py`.

## Monitoring & Observability

**Error Tracking:**
- Custom logging to console and local files (`logs/`).
- Database-backed `SyncLog` and `AIModelPerformance` tracking.

**Logs:**
- Standard Python `logging` with database capture (`TelemetryLog`).

## CI/CD & Deployment

**Hosting:**
- Containerized via Docker / Docker Compose.
- Platform: Typically Linux (Ubuntu) or Windows (via WSL2).

**CI Pipeline:**
- GitHub Actions - Defined in `.github/workflows/`:
  - `ci.yml`: Lints and runs tests.
  - `pre-commit.yml`: Enforces quality on PRs.
  - `close-issues.yml`: Automation for issue management.

## Environment Configuration

**Required env vars:**
- `SECRET_KEY`: Flask app secret for session signing.
- `DATABASE_URL`: SQL database connection URI.
- `LLM_BASE_URL`: OpenAI-compatible endpoint for reasoning.
- `LLM_MODEL_NAME`: Name of the LLM model to use (e.g., `llama3.1`).
- `YOUTUBE_API_KEY`: Key for fetching Reels.
- `TTS_BASE_URL` / `STT_BASE_URL`: Endpoints for audio services.

**Secrets location:**
- Stored in a `.env` file (local dev) or injected via Docker environment variables.

## Webhooks & Callbacks

**Incoming:**
- None detected.

**Outgoing:**
- None detected.

---

*Integration audit: 2025-02-15*
