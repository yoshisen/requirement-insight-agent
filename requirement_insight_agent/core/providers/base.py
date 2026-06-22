"""Abstract interfaces for provider-agnostic chat and embedding access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse


class ChatProvider(ABC):
    """Common interface for chat completion backends."""

    provider_name: str

    @abstractmethod
    def complete(self, request: ChatRequest) -> ChatResponse:
        """Execute one chat completion call."""


class EmbeddingProvider(ABC):
    """Common interface for embedding backends."""

    provider_name: str

    @abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Execute one embedding call."""