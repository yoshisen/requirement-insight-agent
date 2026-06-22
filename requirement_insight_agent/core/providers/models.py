"""Provider-agnostic request and response models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessage(BaseModel):
    """One message in a normalized chat completion request."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    """Provider-neutral chat request payload."""

    model_config = ConfigDict(extra="forbid")

    messages: list[ChatMessage]
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: list[ChatMessage]) -> list[ChatMessage]:
        if not value:
            raise ValueError("messages must contain at least one item")
        return value


class ProviderUsage(BaseModel):
    """Normalized usage metadata returned by a model provider."""

    model_config = ConfigDict(extra="allow")

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class ChatChoice(BaseModel):
    """One assistant choice in a normalized chat response."""

    model_config = ConfigDict(extra="forbid")

    index: int = 0
    message: ChatMessage
    finish_reason: str | None = None


class ChatResponse(BaseModel):
    """Provider-neutral chat response payload."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    output_text: str
    choices: list[ChatChoice]
    usage: ProviderUsage | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    """Provider-neutral embedding request payload."""

    model_config = ConfigDict(extra="forbid")

    texts: list[str]
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("texts must contain at least one item")
        return value


class EmbeddingVector(BaseModel):
    """One embedding vector aligned with one input text."""

    model_config = ConfigDict(extra="forbid")

    index: int
    text: str
    values: list[float]


class EmbeddingResponse(BaseModel):
    """Provider-neutral embedding response payload."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    vectors: list[EmbeddingVector]
    usage: ProviderUsage | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)