# Contributing to Personal Guru

Thank you for your interest in contributing to Personal Guru! We welcome contributions from the community.

## Agile Development & Community

- **Project Board**: Please see our [Project Board](https://github.com/users/Rishabh-Bajpai/projects/2/views/1) to see the current area of focus before starting work.
- **Discord**: Join our [Discord Channel](https://discord.com/channels/1454702827409641616/1454963523233906950) to chat with the team and other contributors.

## Quick Start

1. **Fork & Clone**

   ```bash
   git clone https://github.com/Rishabh-Bajpai/Personal-Guru.git
   cd Personal-Guru
   
   ```

2. **Set Up Environment**

   ```bash
   conda create -n Personal-Guru python=3.11
   conda activate Personal-Guru
   pip install -e .[dev]
   pre-commit install
   ```

3. **Start Services**

   ```bash
   docker compose up speaches db -d       # PostgreSQL database,  STT and TTS
   python scripts/update_database.py
   python run.py                # Start the app
   ```

## How to Contribute

### 1. Find or Open an Issue

- **Always start with an issue.** Please do not open a PR without a corresponding issue.
- Check [existing issues](https://github.com/Rishabh-Bajpai/Personal-Guru/issues) to see if it's already being worked on.
- If not, create a new issue using one of our templates:
    - **Bug Report**
    - **Feature Request**
    - **Question**

### 2. Branching Strategy

- **`main`**: This is the **Production** branch. It is stable and deployed. **Do NOT submit PRs to main.**
- **`development`**: This is the **active development** branch. All new features and fixes merge here first.

### 3. Code Contributions

1. **Create a feature branch from `development`**

   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style.
   - Add docstrings to new functions.
   - Write tests for new functionality.

3. **Run checks**

   ```bash
   pre-commit run --all-files    # Linting & formatting
   python -m pytest -m unit      # Unit tests
   python -m pytest              # All tests
   ```

4. **Submit a Pull Request**

   - **Target the `development` branch**.
   - Use the **Pull Request Template** to fill in the details.
   - Link related issues (e.g., `Closes #123`).
   - Provide a clear description/screenshots if applicable.

## Code Standards

- **Python**: Formatted with Black, linted with Ruff.
- **Docstrings**: Required for all public functions (checked by Interrogate).
- **Commits**: Use clear, descriptive commit messages.

## Project Structure

```
Personal-Guru/
├── app/                    # Flask application
│   ├── core/              # Core routes, models, extensions
│   ├── modes/             # Learning modes (chat, chapter, quiz, etc.)
│   └── common/            # Shared utilities and agents
├── scripts/               # Development utilities
├── scripts/installation/  # Setup scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
```

## Development Tips

- Use `python scripts/db_viewer.py` to browse the database.
- Check `docs/architecture.md` for system design.

## Help & Funding

- **Get Help**: Open an issue with the **Question** label or ask on [Discord](https://discord.com/channels/1454702827409641616/1454963523233906950).
- **Documentation**: [samosa-ai.com/personal-guru/docs](https://samosa-ai.com/personal-guru/docs)

## Using Code from Other Projects

We value the spirit of Open Source and Free Software, which foster collaboration and code reuse across projects. However, Free Software is not the same as the public domain, and license terms still apply. Not all code can be freely reused in every context.

Before integrating a significant portion of code—or adding new dependencies or libraries—please consult the maintainers to verify license compatibility.

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).

---

Thank you for helping make Personal Guru better! 🙏
