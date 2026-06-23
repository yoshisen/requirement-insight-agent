"""Deterministic local placeholder provider for offline smoke testing."""

from __future__ import annotations

import hashlib
import json

from requirement_insight_agent.core.config import ResolvedProviderConfig

from .base import ChatProvider, EmbeddingProvider
from .models import (
    ChatChoice,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingVector,
)


class LocalPlaceholderProvider(ChatProvider, EmbeddingProvider):
    """Provider implementation that produces deterministic placeholder outputs."""

    provider_name = "local"

    def __init__(self, config: ResolvedProviderConfig) -> None:
        self.config = config

    def complete(self, request: ChatRequest) -> ChatResponse:
        structured_response = request.metadata.get("structured_response")
        if structured_response is not None:
            output_text = json.dumps(structured_response, ensure_ascii=False)
            choice = ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=output_text),
                finish_reason="stop",
            )
            return ChatResponse(
                provider=self.provider_name,
                model=request.model or self.config.chat_model,
                output_text=output_text,
                choices=[choice],
                metadata={"placeholder": True, "structured": True},
            )

        prompt = next((message.content for message in reversed(request.messages) if message.role == "user"), "")
        output_text = (
            f"{self.config.response_prefix} provider={self.provider_name} model="
            f"{request.model or self.config.chat_model} prompt={prompt[:160]}"
        )
        choice = ChatChoice(
            index=0,
            message=ChatMessage(role="assistant", content=output_text),
            finish_reason="stop",
        )
        return ChatResponse(
            provider=self.provider_name,
            model=request.model or self.config.chat_model,
            output_text=output_text,
            choices=[choice],
            metadata={"placeholder": True},
        )

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        vectors = [
            EmbeddingVector(index=index, text=text, values=self._vectorize(text))
            for index, text in enumerate(request.texts)
        ]
        return EmbeddingResponse(
            provider=self.provider_name,
            model=request.model or self.config.embedding_model,
            vectors=vectors,
            metadata={"placeholder": True, "dimension": self.config.embedding_dimension},
        )

    def _vectorize(self, text: str) -> list[float]:
        values: list[float] = []
        seed = text.encode("utf-8")
        while len(values) < self.config.embedding_dimension:
            digest = hashlib.sha256(seed).digest()
            values.extend(byte / 255 for byte in digest)
            seed = digest
        return values[: self.config.embedding_dimension]