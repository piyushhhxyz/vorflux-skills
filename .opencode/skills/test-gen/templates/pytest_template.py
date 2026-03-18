"""
pytest template — fill in TODOs and remove this docstring.
Run: pytest test_<module>.py -v --cov=<module> --cov-report=term-missing
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
# from <module> import <ClassOrFunction>


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """Mock database session."""
    db = MagicMock()
    db.query.return_value = db
    db.filter.return_value = db
    db.first.return_value = None
    return db


@pytest.fixture
def mock_http():
    """Mock HTTP client."""
    client = MagicMock()
    client.get.return_value  = MagicMock(status_code=200, json=lambda: {})
    client.post.return_value = MagicMock(status_code=201, json=lambda: {})
    return client


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    """Reset environment variables for each test."""
    monkeypatch.setenv("ENV", "test")


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestMyFunction:

    def test_happy_path(self):
        # result = my_function("valid_input")
        # assert result == expected_value
        pass

    def test_returns_correct_type(self):
        # assert isinstance(result, ExpectedType)
        pass

    @pytest.mark.parametrize("input,expected", [
        ("case_1", "expected_1"),
        ("case_2", "expected_2"),
        ("",       None),
    ])
    def test_parametrized(self, input, expected):
        # result = my_function(input)
        # assert result == expected
        pass

    def test_raises_on_none_input(self):
        with pytest.raises(ValueError):
            pass  # my_function(None)

    def test_raises_on_empty_string(self):
        with pytest.raises((ValueError, KeyError)):
            pass  # my_function("")


# ── Integration tests ─────────────────────────────────────────────────────────

class TestMyFunctionIntegration:

    @patch("module.dependency.external_call")
    def test_calls_dependency(self, mock_call):
        mock_call.return_value = {"key": "value"}
        # my_function("input")
        mock_call.assert_called_once_with("expected_arg")

    @pytest.mark.asyncio
    async def test_async_function(self):
        # result = await my_async_function("input")
        # assert result is not None
        pass
