import pytest
from unittest.mock import patch, MagicMock

# Mark all tests in this file as 'unit'
pytestmark = pytest.mark.unit

def test_chapter_mode_no_plan_direct_access(auth_client, mocker, logger):
    """Test accessing chapter learn mode directly when no plan exists."""
    logger.section("test_chapter_mode_no_plan_direct_access")
    topic_name = "flashcard_only_topic"

    # Topic data with flashcards but no plan
    topic_data = {
        "name": topic_name,
        "plan": [],
        "chapter_mode": [],
        "flashcard_mode": [{"term": "Foo", "definition": "Bar"}]
    }

    mocker.patch('app.modes.chapter.routes.load_topic', return_value=topic_data)

    # 1. Accessing learn mode directly should return 404
    logger.step("GET /chapter/learn/... without plan")
    response = auth_client.get(f'/chapter/learn/{topic_name}/0')
    assert response.status_code == 404
    assert b"Invalid step index" in response.data

def test_chapter_mode_generates_plan_if_missing(auth_client, mocker, logger):
    """Test that accessing the main chapter route generates a plan if missing."""
    logger.section("test_chapter_mode_generates_plan_if_missing")
    topic_name = "flashcard_only_topic"

    # Initial topic data: no plan
    topic_data_initial = {
        "name": topic_name,
        "plan": [],
        "chapter_mode": [],
        "flashcard_mode": [{"term": "Foo", "definition": "Bar"}]
    }

    # Mock load_topic to return initial data
    mocker.patch('app.modes.chapter.routes.load_topic', return_value=topic_data_initial)

    # Mock PlannerAgent to generate a plan
    mocker.patch('app.common.agents.PlannerAgent.generate_study_plan', return_value=['Step 1', 'Step 2'])

    # Mock save_topic
    mock_save = mocker.patch('app.modes.chapter.routes.save_topic')

    # Access /chapter/<topic>
    logger.step(f"GET /chapter/{topic_name}")
    response = auth_client.get(f'/chapter/{topic_name}')

    # Should call planner
    # Should save topic with new plan
    assert mock_save.called
    saved_data = mock_save.call_args[0][1]
    assert saved_data['plan'] == ['Step 1', 'Step 2']

    # Should redirect to learn mode
    assert response.status_code == 302
    assert response.headers['Location'] == f'/chapter/learn/{topic_name}/0'
