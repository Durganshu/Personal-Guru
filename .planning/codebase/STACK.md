# Technology Stack

**Analysis Date:** 2025-02-15

## Languages

**Primary:**
- Python >= 3.9 - Core backend logic, API services, and data processing.

**Secondary:**
- JavaScript (ES6+) - Frontend interactivity and YouTube Iframe API integration.
- HTML5/CSS3 - User interface and responsive design.

## Runtime

**Environment:**
- Python 3.9+
- Gunicorn 23.0.0 - Production WSGI HTTP Server.

**Package Manager:**
- setuptools - Managed via `pyproject.toml`.
- Lockfile: Missing (relying on `pyproject.toml` dependencies).

## Frameworks

**Core:**
- Flask 3.1.0 - Primary web framework.
- Flask-SQLAlchemy 3.1.1 - ORM for database interactions.
- Flask-Migrate 4.0.7 - Database migrations (Alembic).
- Flask-Login 0.6.3 - User session management.
- Flask-Session 0.8.0 - Server-side session storage (filesystem).
- Flask-WTF 1.2.2 - Form handling and CSRF protection.

**Testing:**
- pytest 8.3.4 - Primary testing framework.
- pytest-mock 3.14.0 - Mocking library for tests.
- pytest-cov - Test coverage reporting.

**Build/Dev:**
- ruff - Fast Python linter and formatter.
- pre-commit - Git hooks for code quality.
- pydoc-markdown 4.8.2 - Documentation generation from docstrings.
- Flasgger 0.9.7.1 - Swagger/OpenAPI documentation for Flask.

## Key Dependencies

**Critical:**
- `openai` 2.14.0 - Client for LLM (Ollama/OpenAI), TTS, and STT services.
- `requests` 2.32.3 - HTTP client for external API integrations.
- `google-api-python-client` 2.159.0 - YouTube Data API v3 integration.
- `psycopg2-binary` 2.9.10 - PostgreSQL database adapter.
- `pgvector` 0.3.6 - Vector similarity search support for PostgreSQL.

**Infrastructure:**
- `python-dotenv` 1.0.1 - Environment variable management.
- `Authlib` 1.4.0 - JWE (JSON Web Encryption) and OAuth support.
- `WeasyPrint` 63.1 - PDF generation from HTML.
- `faster-whisper` 1.0.3 - Local high-performance STT (optional).
- `psutil` 6.1.1 - System and process utilities for telemetry.

## Configuration

**Environment:**
- Configured via `.env` file and system environment variables.
- Critical configs: `SECRET_KEY`, `DATABASE_URL`, `LLM_BASE_URL`, `LLM_MODEL_NAME`, `TTS_BASE_URL`, `STT_BASE_URL`, `YOUTUBE_API_KEY`.

**Build:**
- `pyproject.toml`: Primary project configuration and dependency specification.
- `Dockerfile`: Containerization setup.
- `docker-compose.yml`: Multi-container orchestration (App, DB, Speaches).

## Platform Requirements

**Development:**
- Python 3.9+ or Docker Desktop.
- FFmpeg (system dependency for audio processing).

**Production:**
- Docker / Docker Compose.
- PostgreSQL 15.
- Speaches AI (for local TTS/STT).

---

*Stack analysis: 2025-02-15*
