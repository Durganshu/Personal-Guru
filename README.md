# Personalized Learning AI App

This is a Flask-based web application that serves as a proof-of-concept for a personalized learning tool. It uses a multi-agent AI system to create an interactive learning experience tailored to the user's chosen topic.

# For live demo

 [https://pg-demo.samosa-ai.com/](https://pg-demo.samosa-ai.com)
Use desktop computer for the best experience.

## Application Highlights

- **User Accounts:** Secure sign-up, login, and profile management.
- **Dynamic Study Plans:** Custom, step-by-step study plans for any topic.
- **Interactive Learning:** Detailed content, text-to-speech, and progress tracking.
- **Multi-Modal:** Includes Podcast Generation, Flashcards, and Reel Mode (educational shorts).
- **Voice Interaction:** Full voice support for navigation and Q&A.
- **Code Sandbox:** Secure execution of Python code for interactive learning.
- **Knowledge Assessment:** Adaptive quizzes and immediate feedback.
- **Local AI Integration:** Support for local LLMs (Ollama, LM Studio) and TTS (Kokoro).
- **Export options:** Export courses to Markdown files.

**[Features Overview](docs/features.md)**: A detailed breakdown of all application features.

## Installation

### 1. Easy Installation (Recommended)
**Benefits:** One-click setup, no prerequisites, runs entirely offline.

You can download the latest `.exe` installer for Windows from our **[Releases Page](https://github.com/Rishabh-Bajpai/Personal-Guru/releases)**. This bundles everything you need to run the application effortlessly. It automatically handles dependencies, database setup, and application startup.

> **Note:** The `.exe` version does not currently support Text-to-Speech (TTS). To enable TTS or use external APIs, please follow the **[Advanced Installation Guide](docs/installation.md)**.

### 2. Advanced / Developer Installation
**Benefits:** Full feature set (including TTS), customization (External APIs), and development capabilities.

If you want to run the application using Docker, connect to external APIs (like OpenAI for LLM/STT/TTS), or contribute to the code, please refer to our detailed **[Installation Guide](docs/installation.md)**.

## Documentation

- **[Installation Guide](docs/installation.md)**: Detailed setup instructions (Docker, Manual, External APIs).
- **[Developer Setup](docs/setup-developer.md)**: Detailed guide for contributors (includes "Hybrid Mode", utility scripts, and pre-commit hooks).
- **[Architecture](docs/architecture.md)**: High-level system design (C4 Model).
- **[Database Schema](docs/database.md)**: Database tables and migration guide.
- **API Documentation**: Interactive Swagger UI available at `/apidocs/` after running the app.

## Project & Community

- **[Contributing](CONTRIBUTING.md)**: Learn how to set up the dev environment and submit PRs.
- **[Security Policy](SECURITY.md)**: Read about how we handle security and report vulnerabilities.
- **[License](LICENSE)**: Released under the AGPL-3.0 License.
