"""Tests for quiz solver."""

import pytest
import asyncio
from pathlib import Path

from src.solver.quiz_solver import QuizSolver
from src.solver.browser_handler import BrowserHandler
from src.utils.helpers import Timer


@pytest.mark.asyncio
async def test_browser_handler():
    """Test browser handler initialization and navigation."""
    async with BrowserHandler() as browser:
        success = await browser.navigate_to("https://example.com")
        assert success is True
        
        content = await browser.get_page_content()
        assert len(content) > 0
        assert "Example Domain" in content


@pytest.mark.asyncio
async def test_timer():
    """Test timer functionality."""
    timer = Timer(timeout_seconds=2)
    with timer:
        await asyncio.sleep(1)
        assert not timer.is_timeout()
        assert timer.elapsed() >= 1.0
        assert timer.remaining() <= 1.0


@pytest.mark.asyncio
async def test_quiz_solver_initialization():
    """Test quiz solver initialization."""
    solver = QuizSolver()
    assert solver.llm_client is not None
    assert len(solver.handlers) > 0


@pytest.mark.asyncio
async def test_fetch_quiz_page():
    """Test fetching a quiz page."""
    solver = QuizSolver()
    
    # Test with a simple page
    quiz_data = await solver.fetch_quiz_page("https://example.com")
    assert quiz_data is not None
    assert "content" in quiz_data
    assert "html" in quiz_data


def test_payload_size():
    """Test payload size calculation."""
    from src.utils.helpers import get_payload_size
    
    payload = {
        "email": "test@example.com",
        "secret": "test-secret",
        "url": "https://example.com",
        "answer": 12345
    }
    
    size = get_payload_size(payload)
    assert size > 0
    assert size < 1048576  # Less than 1MB


def test_validate_json():
    """Test JSON validation."""
    from src.utils.helpers import validate_json
    
    assert validate_json('{"key": "value"}') is True
    assert validate_json('invalid json') is False
    assert validate_json('') is False
