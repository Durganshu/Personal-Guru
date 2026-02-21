# Testing Patterns

**Analysis Date:** 2026-02-19

## Test Framework

**Runner:**
- `pytest` 8.3.4
- Config: `pytest.ini`

**Assertion Library:**
- Native `assert` statement

**Run Commands:**
```bash
pytest                 # Run all tests
pytest -m unit         # Run unit tests only
pytest -m integration  # Run integration tests only
pytest --cov=app tests/ # Run coverage
```

## Test File Organization

**Location:**
- `tests/` directory (separate from `app/`)

**Naming:**
- `test_*.py` (e.g., `test_app.py`, `test_integration.py`)

**Structure:**
```
tests/
├── data/              # Test fixtures/data
├── conftest.py        # Shared fixtures/config
├── test_app.py        # Main app tests
├── test_integration.py # External integration tests
└── ...
```

## Test Structure

**Suite Organization:**
```python
import pytest
from unittest.mock import patch, MagicMock

# Mark all tests in this file
pytestmark = pytest.mark.unit

def test_feature_name(auth_client, mocker, logger):
    """Test description."""
    # Setup
    logger.section("test_feature_name")
    mocker.patch('app.module.function', return_value=...)

    # Action
    response = auth_client.get('/endpoint')

    # Assertion
    assert response.status_code == 200
    assert b"Expected Content" in response.data
```

**Patterns:**
- **Markers:** Use `pytest.mark.unit` and `pytest.mark.integration`.
- **Setup:** Handled by fixtures in `conftest.py`.
- **Teardown:** `db.drop_all()` in the `app` fixture handles cleanup after each test.
- **Assertion:** Direct value checks and status code assertions.

## Mocking

**Framework:** `unittest.mock` and `pytest-mock` (`mocker` fixture)

**Patterns:**
```python
# In tests/test_app.py
mocker.patch('app.common.agents.PlannerAgent.generate_study_plan', return_value=['Step 1', 'Step 2'])
```

**What to Mock:**
- LLM API calls (`call_llm`, `Agent.generate_...`)
- Database interactions (when testing routes in isolation)
- External services (TTS, STT, WeasyPrint)
- Background processes (e.g., `SyncManager`)

**What NOT to Mock:**
- Simple utility functions
- Core logic within unit tests (unless isolating dependencies)

## Fixtures and Factories

**Test Data:**
- Simple Python dictionaries for mocked responses.
- `tests/data/` for larger static data.

**Location:**
- `tests/conftest.py`: `app`, `client`, `auth_client`, `logger`.

## Coverage

**Requirements:** `interrogate` requires 80% docstring coverage. Code coverage not strictly enforced but `pytest-cov` is available.

**View Coverage:**
```bash
pytest --cov=app tests/
```

## Test Types

**Unit Tests:**
- Focus on individual functions or isolated routes.
- Use `mocker` extensively to avoid external dependencies.
- Location: `tests/test_app.py`, `tests/test_jwe.py`, etc.

**Integration Tests:**
- Focus on real service interaction (LLM, TTS).
- Require environment variables (e.g., `LLM_BASE_URL`).
- Use `@requires_llm` decorator for safety.
- Location: `tests/test_integration.py`.

**E2E Tests:**
- Simulated in `test_full_learning_flow` by mocking the outer layers but following the user session.

## Common Patterns

**Async/Retry Testing:**
- `retry_agent_call` helper for flaky LLM responses.
```python
result, error = retry_agent_call(agent.generate_quiz, "Math", "beginner", count=2)
```

**Error Testing:**
```python
from app.core.exceptions import ValidationError
with pytest.raises(ValidationError):
    validate_config(invalid_config)
```

---

*Testing analysis: 2026-02-19*
