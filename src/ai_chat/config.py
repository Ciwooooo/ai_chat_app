"""Application configuration using environment variables.

Environment variables are prefixed with AI_CHAT_ to avoid conflicts.
Example: AI_CHAT_LLM_BASE_URL=http://ollama:11434/v1

This allows the same code to run in different environments:
- Local development: uses localhost
- Docker: uses host.docker.internal
- Kubernetes: uses service name (ollama)
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden by setting environment variables
    with the AI_CHAT_ prefix. For example:
        AI_CHAT_LLM_MODEL=mistral
        AI_CHAT_LLM_BASE_URL=http://custom-host:11434/v1
    """

    # Application settings
    app_name: str = "AI Chat"

    # LLM settings - configured for Ollama by default
    # Ollama exposes an OpenAI-compatible API at /v1
    llm_base_url: str = "http://localhost:11434/v1"

    # Model to use - llama3.2:1b is small and fast for testing
    # Other options: llama3.2, mistral, phi3, etc.
    llm_model: str = "llama3.2:1b"

    # Ollama doesn't require an API key, but the OpenAI client
    # expects one, so we provide a dummy value
    llm_api_key: str = "ollama"

    class Config:
        # Prefix for environment variables
        # e.g., AI_CHAT_LLM_MODEL instead of just LLM_MODEL
        env_prefix = "AI_CHAT_"

        # Make settings case-insensitive
        case_sensitive = False


# Create a global settings instance
# This is imported by other modules
settings = Settings()
