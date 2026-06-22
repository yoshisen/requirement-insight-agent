"""Simple provider factory for the MVP runtime."""

from __future__ import annotations

from dataclasses import dataclass

from requirement_insight_agent.core.config import AppConfig, get_settings

from .anthropic import AnthropicProvider
from .base import ChatProvider, EmbeddingProvider
from .exceptions import ProviderConfigurationError
from .gemini import GeminiProvider
from .local import LocalPlaceholderProvider
from .openai import OpenAIProvider


@dataclass(slots=True)
class ProviderStack:
    """Resolved pair of chat and embedding providers."""

    chat: ChatProvider
    embeddings: EmbeddingProvider


def _create_provider(config) -> ChatProvider | EmbeddingProvider:
    if config.provider_name == "openai":
        return OpenAIProvider(config)
    if config.provider_name == "anthropic":
        return AnthropicProvider(config)
    if config.provider_name == "gemini":
        return GeminiProvider(config)
    if config.provider_name == "local":
        return LocalPlaceholderProvider(config)
    raise ProviderConfigurationError(f"Unsupported provider: {config.provider_name}")


def create_provider_stack(settings: AppConfig | None = None) -> ProviderStack:
    """Create the chat and embedding providers from resolved runtime settings."""

    resolved_settings = settings or get_settings()
    return ProviderStack(
        chat=_create_provider(resolved_settings.resolve_chat_provider()),
        embeddings=_create_provider(resolved_settings.resolve_embedding_provider()),
    )