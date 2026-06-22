"""Minimal OpenAI provider implementation.

The MVP intentionally keeps this lightweight: chat completion and embeddings are
implemented via the REST API using the standard library for transport.
"""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request as urllib_request

from requirement_insight_agent.core.config import ResolvedProviderConfig

from .base import ChatProvider, EmbeddingProvider
from .exceptions import ProviderAuthenticationError, ProviderRequestError
from .models import (
    ChatChoice,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingVector,
    ProviderUsage,
)


class OpenAIProvider(ChatProvider, EmbeddingProvider):
    """OpenAI-backed provider for normalized chat and embedding calls."""

    provider_name = "openai"

    def __init__(self, config: ResolvedProviderConfig) -> None:
        self.config = config

    def complete(self, request: ChatRequest) -> ChatResponse:
        payload: dict[str, Any] = {
            "model": request.model or self.config.chat_model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        raw = self._post_json("/chat/completions", payload)
        choice_payload = raw["choices"][0]
        content = self._normalize_content(choice_payload["message"]["content"])
        choice = ChatChoice(
            index=choice_payload.get("index", 0),
            message=ChatMessage(role="assistant", content=content),
            finish_reason=choice_payload.get("finish_reason"),
        )
        return ChatResponse(
            provider=self.provider_name,
            model=payload["model"],
            output_text=content,
            choices=[choice],
            usage=self._extract_usage(raw),
            raw_response=raw,
        )

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        payload = {
            "model": request.model or self.config.embedding_model,
            "input": request.texts,
        }
        raw = self._post_json("/embeddings", payload)
        vectors = [
            EmbeddingVector(index=item["index"], text=request.texts[item["index"]], values=item["embedding"])
            for item in raw.get("data", [])
        ]
        return EmbeddingResponse(
            provider=self.provider_name,
            model=payload["model"],
            vectors=vectors,
            usage=self._extract_usage(raw),
            raw_response=raw,
        )

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.config.api_key is None or not self.config.api_key.get_secret_value():
            raise ProviderAuthenticationError("OPENAI_API_KEY is required for the OpenAI provider")
        request_url = f"{(self.config.base_url or '').rstrip('/')}{path}"
        req = urllib_request.Request(
            request_url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib_request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderRequestError(f"OpenAI request failed: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise ProviderRequestError(f"OpenAI request failed: {exc.reason}") from exc

    @staticmethod
    def _normalize_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
        return str(content)

    @staticmethod
    def _extract_usage(raw: dict[str, Any]) -> ProviderUsage | None:
        usage = raw.get("usage")
        if not isinstance(usage, dict):
            return None
        return ProviderUsage(
            input_tokens=usage.get("prompt_tokens") or usage.get("input_tokens"),
            output_tokens=usage.get("completion_tokens") or usage.get("output_tokens"),
            total_tokens=usage.get("total_tokens"),
        )