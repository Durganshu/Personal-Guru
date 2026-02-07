# Software Architecture

This document describes the high-level architecture of the Personal Guru application using the C4 model.

## 1. System Context Diagram (Level 1)

Personal Guru provides a personalized learning experience by orchestrating multiple AI services and local processing.

```mermaid
C4Context
    title System Context Diagram for Personal Guru

    Person(user, "User", "A learner seeking personalized study material.")
    System(personal_guru, "Personal Guru", "Generates study plans, content, quizzes, and multimedia.")

    System_Ext(llm, "LLM Provider", "Gemini / OpenAI / Groq / Ollama / LMStudio")
    System_Ext(youtube, "YouTube", "Provides video content for Reel Mode.")
    System_Ext(dcs, "Data Collection Server (DCS)", "Handles telemetry and distributed sync.")
    System_Ext(audio_ext, "External Audio API", "OpenAI-compatible TTS/STT endpoints.")

    Rel(user, personal_guru, "Uses", "HTTPS")
    Rel(personal_guru, llm, "Generates Content", "JSON/REST")
    Rel(personal_guru, youtube, "Search & Embeds", "API")
    Rel(personal_guru, dcs, "Syncs Data & Telemetry", "HTTPS/REST")
    Rel(personal_guru, audio_ext, "TTS/STT (Optional)", "REST")
```

## 2. Container Diagram (Level 2)

The system consists of a Flask web application, a relational database, and several background services.

```mermaid
C4Container
    title Container Diagram for Personal Guru

    Person(user, "User", "Learner")

    Container_Boundary(c1, "Personal Guru System") {
        Container(web_app, "Web Application", "Python, Flask", "Handles user requests, coordinates agents, and renders UI.")
        ContainerDb(db, "Relational Database", "SQLite/SQLAlchemy", "Stores users, topics, content, and telemetry.")
        Container(background_services, "Background Services", "Threaded", "SyncManager, AudioService, Code Sandbox.")
    }

    System_Ext(llm, "LLM Provider", "AI Intelligence")
    System_Ext(dcs, "DCS", "Telemetry & Sync")

    Rel(user, web_app, "Interacts with", "HTTPS/HTML")
    Rel(web_app, db, "Reads/Writes", "SQLAlchemy")
    Rel(web_app, background_services, "Manages", "In-process threads")
    Rel(background_services, db, "Syncs/Updates", "SQLAlchemy")
    Rel(web_app, llm, "Calls", "JSON/REST")
    Rel(background_services, dcs, "Reports to", "HTTPS")
```

## 3. Component Diagram (Level 3)

The Web Application is organized into modular Blueprints and Core services.

```mermaid
C4Component
    title Component Diagram - Web Application

    Container_Boundary(blueprints, "Feature Blueprints (app/modes)") {
        Component(chapter_bp, "Chapter Mode", "Blueprint", "Learning content & podcasts.")
        Component(quiz_bp, "Quiz Mode", "Blueprint", "Assessments & grading.")
        Component(flashcard_bp, "Flashcard Mode", "Blueprint", "Study cards generation.")
        Component(reel_bp, "Reel Mode", "Blueprint", "YouTube short discovery.")
        Component(chat_bp, "Chat", "Blueprint", "Interactive AI guidance.")
    }

    Container_Boundary(core, "Core Services (app/core)") {
        Component(models, "Models", "SQLAlchemy", "Database schema definitions.")
        Component(routes_main, "Main Routes", "Blueprint", "Auth, Home, Settings.")
        Component(ext, "Extensions", "Flask", "Auth, DB, Migrate, Swagger.")
    }

    Container_Boundary(common, "Common Utilities (app/common)") {
        Component(sync_mgr, "SyncManager", "DCS", "Background data synchronization.")
        Component(audio_svc, "AudioService", "TTS/STT", "Unified audio interface.")
        Component(sandbox, "Sandbox", "Venv", "Secure code execution environment.")
        Component(agents, "Agents", "Classes", "Planner, Teacher, Assessor Agents.")
    }

    Rel(chapter_bp, agents, "Uses")
    Rel(quiz_bp, agents, "Uses")
    Rel(chat_bp, agents, "Uses")
    Rel(chapter_bp, audio_svc, "Requests Audio")
    Rel(sync_mgr, models, "Syncs")
    Rel(routes_main, ext, "Uses")

    Rel(chapter_bp, models, "Persists to")
    Rel(quiz_bp, models, "Persists to")
    Rel(flashcard_bp, models, "Persists to")
    Rel(chat_bp, models, "Persists to")
    Rel(routes_main, models, "Persists to")
```

## 4. Data Model (Entity Relationship Diagram)

Personal Guru uses a structured relational model to track learning progress and application state.

```mermaid
erDiagram
    LOGIN ||--o| USER : "has profile"
    LOGIN ||--o{ TOPIC : "owns"
    TOPIC ||--o{ CHAPTER_MODE : "contains"
    TOPIC ||--o| QUIZ_MODE : "has"
    TOPIC ||--o{ FLASHCARD_MODE : "contains"
    TOPIC ||--o| CHAT_MODE : "has history"
    TOPIC ||--o{ PLAN_REVISION : "tracks changes"
    INSTALLATION ||--o{ LOGIN : "hosts"
    INSTALLATION ||--o{ TELEMETRY_LOG : "generates"
    INSTALLATION ||--o{ SYNC_LOG : "records"

    LOGIN {
        string userid PK
        string username
        string password_hash
    }
    TOPIC {
        int id PK
        string name
        json study_plan
    }
    CHAPTER_MODE {
        int topic_id FK
        int step_index
        string content
        string audio_path
    }
    USER {
        string login_id FK
        string education_level
        string learning_goals
    }
```

## 5. Dynamic Views (Sequence Diagrams)

### 5.1 Study Step Loading & Generation

Previously, the system relied on JSON files. Now, it uses a database-first approach with lazy generation of AI content.

```mermaid
sequenceDiagram
    participant User
    participant App as "Chapter Blueprint"
    participant DB as "SQLite DB"
    participant Teacher as "TeacherAgent"
    participant LLM

    User->>App: GET /chapter/<topic_id>/<step>
    App->>DB: Query ChapterMode
    alt Content exists in DB
        DB-->>App: Return cached content
    else Content missing
        App->>Teacher: generate_material(Context)
        Teacher->>LLM: JSON/REST Request
        LLM-->>Teacher: Markdown/JSON Response
        Teacher-->>App: Content Object
        App->>DB: Save to ChapterMode
    end
    App-->>User: Render learning interface
```

### 5.2 Background Data Synchronization

```mermaid
sequenceDiagram
    participant App as "SyncManager (Thread)"
    participant DB as "SQLite DB"
    participant DCS as "Remote DCS Server"

    loop Every 60 seconds
        App->>DB: Query unsynced records (sync_status='pending')
        DB-->>App: List of records
        App->>DCS: POST /api/sync (Payload)
        DCS-->>App: HTTP 200 OK
        App->>DB: Update records to sync_status='synced'
        App->>DB: Log sync success in SyncLog
    end
```
