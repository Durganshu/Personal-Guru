# Coding Conventions

**Analysis Date:** 2026-02-19

## Naming Patterns

**Files:**
- Python: snake_case (e.g., `setup_app.py`, `utils.py`)
- Javascript: snake_case or kebab-case (e.g., `base.js`, `mode-buttons-refined.css`)
- Templates: snake_case (e.g., `index.html`, `login.html`)

**Functions:**
- Python: snake_case (e.g., `call_llm`, `get_all_topics`)
- Javascript: camelCase (e.g., `setupFloatingIcons`, `showLoader`)

**Variables:**
- Python: snake_case (e.g., `topic_name`, `error_code`)
- Python Constants: UPPER_SNAKE_CASE (e.g., `LLM_BASE_URL`, `TTS_MODEL`)
- Javascript: camelCase (e.g., `loaderText`, `factText`)

**Types/Classes:**
- Python: PascalCase (e.g., `PlannerAgent`, `MockPagination`, `MissingConfigError`)

## Code Style

**Formatting:**
- Tool: `ruff` (used via `pre-commit`)
- Settings: Defined in `pyproject.toml` (`[tool.ruff]`)
- Style: Follows PEP 8 with some ignores (e.g., `E501` - line length)

**Linting:**
- Tool: `ruff` for Python, `codespell` for spelling
- Key rules: `select = ["E", "F"]` (standard linting and pyflakes errors)
- Docstring Coverage: `interrogate` ensures docstring presence (fail-under=80)

## Import Organization

**Order:**
1. Standard library (e.g., `os`, `sys`, `time`)
2. Third-party packages (e.g., `flask`, `requests`, `openai`)
3. Local application imports (e.g., `from app.core.models import db`)

**Path Aliases:**
- Not used; absolute imports starting from `app` (e.g., `from app.common.utils import ...`) are standard.

## Error Handling

**Patterns:**
- Custom exceptions defined in `app/core/exceptions.py` (e.g., `LLMConnectionError`, `MissingConfigError`).
- Use of `try-except` blocks for external service calls (LLM, TTS, DB).
- Graceful failure for non-critical operations (e.g., telemetry/cleanup) with `pass` and logger warning.
- Exceptions often include descriptive messages and custom error codes.

## Logging

**Framework:** Python `logging` module.

**Patterns:**
- Loggers initialized with `logger = logging.getLogger(__name__)`.
- Log messages use f-strings or standard formatting.
- `log_telemetry` helper in `app/common/utils.py` for structured event tracking.

## Comments

**When to Comment:**
- Descriptive comments for complex logic blocks.
- Docstrings for all functions, classes, and modules.
- Markers for `TODO` or `HACK` where applicable.

**JSDoc/TSDoc:**
- Basic Javascript comments for function descriptions.
- Markdown docstrings for Python following Sphinx-like format with `Raises:` and `Args:` (though not strictly enforced).

## Function Design

**Size:** Functions are generally kept focused on a single responsibility.

**Parameters:** Mix of positional and keyword arguments. Type hints are encouraged but not consistently used in all older files.

**Return Values:** Functions often return structured data (lists, dicts) or specific objects. Agents often return a `(result, error)` tuple pattern for better error handling.

## Module Design

**Exports:** Flask Blueprints are used to organize routes by feature/mode (`app/modes/chapter/routes.py`, `app/core/routes.py`).

**Barrel Files:** `__init__.py` files are present in every package to facilitate imports and sometimes to initialize components.

---

*Convention analysis: 2026-02-19*
