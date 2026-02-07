# Database Documentation

This document details the database structure and management for the Personal Guru application.

## Database Engine

Personal Guru uses **SQLite** as its default database engine for ease of local setup and portability. The application uses **SQLAlchemy** as an Object-Relational Mapper (ORM) to interact with the database.

> [!NOTE]
> In Docker environments, the database file is typically stored in the `instance/` directory, which should be persisted using a volume.

## Database Schema

The core models are defined in `app/core/models.py`.

### Primary Tables

| Table Name | Description |
| :--- | :--- |
| `logins` | Stores user credentials, password hashes, and identity IDs. |
| `users` | Stores extended user profiles (education, goals, preferences). |
| `topics` | Represents a learning subject and its overall study plan. |
| `chapter_mode` | Stores AI-generated reading material and questions for study steps. |
| `quiz_mode` | Stores final assessments and results for a topic. |
| `flashcard_mode`| Stores term-definition pairs for a topic. |
| `chat_mode` | Records conversational history for a topic. |

### System & Telemetry Tables

| Table Name | Description |
| :--- | :--- |
| `installations` | Tracks unique application installs and hardware specs. |
| `telemetry_logs`| Records user actions and events for analytics. |
| `sync_logs` | Records background data synchronization attempts. |
| `feedback` | Stores user ratings and comments. |
| `ai_model_performance` | Tracks LLM latency and token usage metrics. |
| `plan_revisions`| Records changes made to study plans over time. |

## Management & Migrations

Personal Guru uses **Flask-Migrate** (powered by Alembic) for handling database schema changes.

### Running Migrations

1. **Initialize** (only once):

   ```bash
   flask db init
   ```

2. **Generate Migration Script**:

   ```bash
   flask db migrate -m "Description of changes"
   ```

3. **Apply Changes**:

   ```bash
   flask db upgrade
   ```

### Manual Data Management

For developers, a built-in admin tool is available at `/admin/db-viewer` (if enabled) to view and manage records. For raw access, use standard SQLite clients like `sqlite3` or DB Browser for SQLite on the `instance/site.db` file.
