"""Tests for the chat module."""

from unittest.mock import MagicMock, patch

from ai_chat.chat import chat_completion, get_llm_client


def test_get_llm_client():
    """Test LLM client is created."""
    client = get_llm_client()
    assert client is not None


def test_chat_completion_mock():
    """Test chat completion with mocked LLM response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello! How can I help?"

    with patch("ai_chat.chat.get_llm_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response

        result = chat_completion([{"role": "user", "content": "Hi"}])

        assert result == "Hello! How can I help?"
