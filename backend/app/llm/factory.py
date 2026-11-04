from app.core.config import Settings
from app.llm.base import LLMProviderError, LLMProvider
from app.llm.mock import MockProvider


def create_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "mock":
        return MockProvider()
    raise LLMProviderError(
        f"Unsupported LLM provider '{settings.llm_provider}'. "
        "Use LLM_PROVIDER=mock until a configured provider adapter is added."
    )
