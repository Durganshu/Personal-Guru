# Codebase Structure

**Analysis Date:** 2025-02-19

## Directory Layout

```
[project-root]/
├── app/                  # Main application source code
│   ├── common/           # Shared services, agents, and utilities
│   ├── core/             # Core application models, routes, and extensions
│   ├── modes/            # Feature-specific blueprints (Chapter, Quiz, Chat, etc.)
│   ├── static/           # Frontend assets (CSS, JS, images, audio)
│   └── templates/        # Global Jinja2 templates (error pages, base layout)
├── app_DCS/              # (Optional) Standalone Data Collection Service
├── data/                 # Data storage for audio, models, and sandbox
│   ├── audio/            # Generated audio files (podcasts, etc.)
│   ├── models/           # Local AI model storage (Whisper)
│   └── sandbox/          # Temporary environments for code execution
├── docs/                 # Project documentation and ADRs
├── instance/             # Local database and instance-specific config
├── logs/                 # Application log files
├── migrations/           # Alembic/Flask-Migrate database migration scripts
├── scripts/              # Utility scripts for maintenance and setup
├── tests/                # Automated test suite
├── .env                  # Environment variables (not committed)
├── config.py             # Application configuration loading
├── docker-compose.yml    # Docker orchestration
├── Dockerfile            # Container definition
├── pyproject.toml        # Python project metadata and dependencies
└── run.py                # Application entry point
```

## Directory Purposes

**app/common/:**
- Purpose: Shared logic used across multiple blueprints.
- Contains: AI agents, audio service, storage utilities, and telemetry.
- Key files: `app/common/agents.py`, `app/common/utils.py`, `app/common/storage.py`, `app/common/audio_service.py`.

**app/core/:**
- Purpose: Fundamental building blocks of the application.
- Contains: Database models, main routes (login/profile/home), and Flask extensions.
- Key files: `app/core/models.py`, `app/core/routes.py`, `app/core/extensions.py`.

**app/modes/:**
- Purpose: Modular feature blueprints.
- Contains: Each mode (Chapter, Chat, Flashcard, Quiz, Reel) has its own subdirectory with routes, agents, prompts, and templates.
- Key files: `app/modes/chapter/routes.py`, `app/modes/chat/agent.py`.

**data/:**
- Purpose: Persistence for large or binary data.
- Contains: Audio files, machine learning models, and sandboxed execution artifacts.

**scripts/:**
- Purpose: Developer and operational tools.
- Contains: Database maintenance, documentation generation, and installation helpers.
- Key files: `scripts/update_database.py`, `scripts/visualize_db.py`.

## Key File Locations

**Entry Points:**
- `run.py`: Primary entry point for starting the web server.
- `app/__init__.py`: Application factory (`create_app`).
- `app/setup_app.py`: Initial setup wizard for first-time configuration.

**Configuration:**
- `config.py`: Loads environment variables and provides a `Config` class.
- `.env`: (Local only) Stores sensitive configuration like API keys.

**Core Logic:**
- `app/common/utils.py`: Central hub for LLM calls, audio generation, and telemetry.
- `app/common/agents.py`: High-level AI coordination for planning and feedback.
- `app/common/storage.py`: Orchestrates database persistence for complex topic objects.

**Testing:**
- `tests/conftest.py`: Shared test fixtures.
- `tests/test_app.py`: Main application integration tests.

## Naming Conventions

**Files:**
- [snake_case.py]: Python source files (e.g., `audio_service.py`).
- [snake_case.js]: JavaScript frontend logic (e.g., `learn_step.js`).
- [snake_case.css]: CSS stylesheets (e.g., `learning-modes.css`).

**Directories:**
- [snake_case]: Directory names (e.g., `chapter_mode`).

**Variables/Functions:**
- [snake_case]: Standard Python/JS naming (e.g., `generate_audio`).

**Classes:**
- [PascalCase]: Python classes (e.g., `SyncManager`, `TopicTeachingAgent`).

## Where to Add New Code

**New Learning Mode:**
- Implementation: Create a new directory in `app/modes/[mode_name]`.
- Structure: Follow the pattern: `routes.py`, `agent.py`, `prompts.py`, `static/`, `templates/`.
- Registration: Register the blueprint in `app/__init__.py`.

**New Shared Service:**
- Implementation: Add to `app/common/[service_name].py`.
- Integration: Use in relevant agents or routes.

**New Database Model:**
- Implementation: Define in `app/core/models.py`.
- Migration: Run `flask db migrate` and `flask db upgrade`.

**Frontend Assets:**
- Shared: `app/static/`
- Mode-specific: `app/modes/[mode]/static/`

## Special Directories

**flask_session/:**
- Purpose: Server-side session storage files.
- Generated: Yes
- Committed: No

**postgres_data/:**
- Purpose: Persistent storage for PostgreSQL in Docker.
- Generated: Yes
- Committed: No

**build/, dist/, personal_guru.egg-info/:**
- Purpose: Python distribution and packaging artifacts.
- Generated: Yes
- Committed: No

---

*Structure analysis: 2025-02-19*
