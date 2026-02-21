# Architecture

**Analysis Date:** 2025-02-19

## Pattern Overview

**Overall:** Flask Application Factory with Blueprint-based Modularity.

**Key Characteristics:**
- **Modular Design:** Each learning mode (chapter, quiz, chat, etc.) is encapsulated in its own blueprint with dedicated routes, agents, and templates.
- **AI-First Architecture:** Centralized AI service layer (`app/common/agents.py`, `app/common/utils.py`) supporting LLM, TTS, and STT.
- **Background Synchronization:** Periodical data sync with a remote Data Collection Server (DCS) for telemetry and backup.
- **Multi-Tenant Ready:** User isolation implemented at the database level with `user_id` foreign keys.

## Layers

**Application Layer:**
- Purpose: Application lifecycle, configuration, and extension initialization.
- Location: `app/__init__.py`, `app/setup_app.py`, `config.py`
- Contains: Flask factory, extension setup, global error handlers, and blueprint registration.
- Depends on: Core, Common, Modes
- Used by: `run.py`

**Presentation Layer:**
- Purpose: Web interface and API endpoints.
- Location: `app/core/routes.py`, `app/modes/*/routes.py`, `app/static/`, `app/templates/`
- Contains: Flask routes, Jinja2 templates, and frontend assets (JS/CSS).
- Depends on: Core, Common
- Used by: End users via browser

**Service/Agent Layer:**
- Purpose: Business logic and AI interaction.
- Location: `app/common/agents.py`, `app/modes/*/agent.py`
- Contains: Specialized AI agents (Planner, Chat, Feedback, Suggestion) and business logic.
- Depends on: Common Utilities, Core Models
- Used by: Presentation Layer (Routes)

**Data Access Layer (Storage):**
- Purpose: Persistence and retrieval of application data.
- Location: `app/common/storage.py`, `app/core/models.py`, `app/core/extensions.py`
- Contains: SQLAlchemy models, migration scripts (Alembic), and high-level storage utilities.
- Depends on: SQLAlchemy, Flask-SQLAlchemy
- Used by: Service Layer, Presentation Layer

**Infrastructure/Common Layer:**
- Purpose: Shared utilities and external integrations.
- Location: `app/common/utils.py`, `app/common/audio_service.py`, `app/common/dcs.py`, `app/common/sandbox.py`
- Contains: LLM/TTS/STT wrappers, telemetry logging, background sync, and code execution sandbox.
- Depends on: External APIs (OpenAI, etc.), System OS
- Used by: All layers

## Data Flow

**Learning Content Generation:**

1. User submits a topic via `app/core/routes.py`.
2. `PlannerAgent` in `app/common/agents.py` calls `call_llm` in `app/common/utils.py` to generate a study plan.
3. Plan is saved via `save_topic` in `app/common/storage.py`.
4. For each step, `ChapterMode` agent generates teaching material and assessments.
5. Content is rendered to the user via mode-specific templates.

**Background Synchronization:**

1. `SyncManager` in `app/common/dcs.py` starts a background thread.
2. It periodically queries the database for records with `sync_status = 'pending'`.
3. `DCSClient` batches and sends data to the remote DCS API.
4. On success, local records are marked as `synced`.

**State Management:**
- **Database:** PostgreSQL (production) or SQLite (local) managed via SQLAlchemy.
- **Sessions:** Server-side sessions using `flask-session` to store large chat histories and transient state (like `sandbox_id`).
- **Filesystem:** Local storage for generated audio files in `app/static/`.

## Key Abstractions

**Agent Interface:**
- Purpose: Standardizes AI interactions for different tasks.
- Examples: `CodeExecutionAgent`, `FeedbackAgent`, `PlannerAgent`, `ChatAgent` in `app/common/agents.py`.
- Pattern: Strategy/Command pattern for different AI behaviors.

**Audio Service Abstraction:**
- Purpose: Unified interface for TTS and STT, supporting both local (Whisper) and remote (OpenAI-compatible) providers.
- Examples: `TTSService`, `STTService` in `app/common/audio_service.py`.
- Pattern: Adapter pattern.

**Sync Mixin:**
- Purpose: Provides standard synchronization fields for models.
- Examples: `SyncMixin` in `app/core/models.py`.

## Entry Points

**Web Server:**
- Location: `run.py`
- Triggers: Manual execution or container start.
- Responsibilities: Loads environment, validates config, initializes the Flask app, and starts the development server.

**Setup Wizard:**
- Location: `app/setup_app.py`
- Triggers: `run.py` if mandatory configuration is missing.
- Responsibilities: Provides a web interface for initial configuration and `.env` generation.

## Error Handling

**Strategy:** Centralized exception hierarchy with automated logging and standardized API/UI responses.

**Patterns:**
- **Custom Exceptions:** Defined in `app/core/exceptions.py` (e.g., `PersonalGuruException`, `LLMError`, `DatabaseError`).
- **Global Error Handlers:** Registered in `app/__init__.py` using `@app.errorhandler`.
- **JSON vs HTML Response:** Logic in error handlers to return appropriate format based on request headers.

## Cross-Cutting Concerns

**Logging:** Standard Python `logging` module with per-module loggers.
**Telemetry:** `log_telemetry` utility in `app/common/utils.py` for tracking user actions and system performance.
**Authentication:** `Flask-Login` for session management and Dual Token Security (CSRF + JWE) for state-changing requests.
**Security:** JWE (JSON Web Encryption) used for securing state-changing requests, enforced in `main_bp.before_app_request`.

---

*Architecture analysis: 2025-02-19*
