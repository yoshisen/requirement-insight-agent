"""Gemini provider placeholder for the MVP scaffold."""

from __future__ import annotations

from requirement_insight_agent.core.config import ResolvedProviderConfig

from .base import ChatProvider, EmbeddingProvider
from .exceptions import ProviderNotImplementedError
from .models import ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse


class GeminiProvider(ChatProvider, EmbeddingProvider):
    """Provider stub for future Gemini integration."""

    provider_name = "gemini"

    def __init__(self, config: ResolvedProviderConfig) -> None:
        self.config = config

    def complete(self, request: ChatRequest) -> ChatResponse:
        raise ProviderNotImplementedError("Gemini chat execution is not implemented in the MVP scaffold")

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise ProviderNotImplementedError("Gemini embeddings are not implemented in the MVP scaffold")