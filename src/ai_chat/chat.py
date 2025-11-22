"""LLM communication module.

This module handles all interactions with the language model.
It uses the OpenAI client library to communicate with Ollama's
OpenAI-compatible API endpoint.

Ollama serves an OpenAI-compatible API at http://localhost:11434/v1
This means we can use the standard OpenAI Python client, which is
well-documented and widely used.
"""

from openai import OpenAI

from ai_chat.config import settings


def get_llm_client() -> OpenAI:
    """Create an OpenAI-compatible client configured for Ollama.
    
    Returns:
        OpenAI client instance pointing to the configured LLM server.
    
    Example:
        client = get_llm_client()
        response = client.chat.completions.create(...)
    """
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,  # Ollama ignores this but client requires it
    )


def chat_completion(messages: list[dict[str, str]]) -> str:
    """Send a conversation to the LLM and get a response.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys.
                  Roles are typically 'user', 'assistant', or 'system'.
                  Example: [
                      {"role": "user", "content": "Hello!"},
                      {"role": "assistant", "content": "Hi there!"},
                      {"role": "user", "content": "How are you?"}
                  ]
    
    Returns:
        The assistant's response as a string.
    
    Raises:
        Exception: If the LLM request fails (connection error, timeout, etc.)
    
    Example:
        messages = [{"role": "user", "content": "What is Python?"}]
        response = chat_completion(messages)
        print(response)  # "Python is a programming language..."
    """
    client = get_llm_client()
    
    # Call the chat completions endpoint
    # This is the same API format as OpenAI's GPT models
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,  # type: ignore[arg-type]
        temperature=0.7,    # Controls randomness (0=deterministic, 1=creative)
        max_tokens=1024,    # Maximum length of response
    )
    
    # Extract the text content from the response
    # The response structure matches OpenAI's format:
    # response.choices[0].message.content
    content = response.choices[0].message.content
    
    # Return empty string if content is None (shouldn't happen normally)
    return content or ""