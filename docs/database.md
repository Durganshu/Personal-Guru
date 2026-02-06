# Database Documentation

This document details the database structure and management for the Personal Guru application.

## Database Schema

The application uses the following PostgreSQL tables:

- **users**: Stores user accounts and profiles.
- **topics**: Main table for each subject the user is learning.
- **study_steps**: Steps within a study plan (one-to-many from topics).
- **quizzes**: Quizzes generated for a topic.
- **flashcards**: Flashcards for vocabulary terms.
- **chat_sessions**: Stores the conversational history for "Chat Mode" (one-to-one with topics). Note: "Chapter Mode" side-chats are stored directly in `study_steps.chat_history`.

## Database Migration (Recommended Safe Method)

If you plan to move data between different types of computers (e.g., your Linux server to a Windows laptop), it is safer to use the built-in backup tools:

1. **Export (on old machine):**

   ```bash
   docker compose exec db pg_dump -U postgres personal_guru > backup.sql
   ```

2. **Import (on new machine):**
   Move the `backup.sql` file to the new machine, start the fresh empty container, and run:

   ```bash
   # Copy file into container
   docker cp backup.sql personal-guru-db-1:/backup.sql

   # Restore
   docker compose exec db psql -U postgres -d personal_guru -f /backup.sql
   ```
