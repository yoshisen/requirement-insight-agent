"""Runtime configuration loader for model and provider selection.

This module merges TOML presets under `configs/models/` with environment-based
overrides. Environment variables win over preset values.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
import tomllib

from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from requirement_insight_agent.project import PROJECT_ROOT


ProviderName = Literal["openai", "anthropic", "gemini", "local"]
RoutingStrategy = Literal["single_provider", "cost_performance_routing"]

DEFAULT_MODEL_CONFIG_PATH = PROJECT_ROOT / "configs" / "models" / "default.toml"
DEFAULT_PROVIDER_CONFIG_DIR = PROJECT_ROOT / "configs" / "providers"


class RoutingConfig(BaseModel):
    """Routing settings for future provider fallback and cost/performance logic."""

    strategy: RoutingStrategy = "single_provider"
    fallback_order: list[ProviderName] = Field(default_factory=list)
    enable_fallback: bool = False


class OpenAIProviderConfig(BaseModel):
    """OpenAI-specific connection options."""

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    organization: str | None = None
    project: str | None = None


class PlaceholderProviderConfig(BaseModel):
    """Placeholder config for future external providers."""

    api_key: str | None = None
    enabled: bool = False
    api_base: str | None = None


class LocalProviderConfig(BaseModel):
    """Local deterministic provider settings used for smoke tests and offline development."""

    chat_model: str = "local-chat-placeholder"
    embedding_model: str = "local-embedding-placeholder"
    embedding_dimensions: int = Field(default=8, ge=1)
    response_prefix: str = "[local]"


class ProviderPreset(BaseModel):
    """Checked-in provider preset used as a shared default template."""

    provider_name: ProviderName
    default_chat_model: str | None = None
    default_embedding_model: str | None = None
    base_url: str | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 2
    supports_chat: bool = True
    supports_embeddings: bool = True
    embedding_dimension: int | None = None


class ResolvedProviderConfig(BaseModel):
    """Resolved runtime configuration for a chat or embedding provider."""

    provider_name: ProviderName
    chat_model: str
    embedding_model: str
    base_url: str | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 2
    routing_strategy: RoutingStrategy = "single_provider"
    embedding_dimension: int = 8
    response_prefix: str = "[local]"
    api_key: SecretStr | None = None


class AppConfig(BaseModel):
    """Merged runtime configuration used by provider factories and CLI commands."""

    model_provider: ProviderName = "local"
    embedding_provider: ProviderName | None = None
    chat_model: str = "local-chat-placeholder"
    embedding_model: str = "local-embedding-placeholder"
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1)
    request_timeout_seconds: float = Field(default=30.0, gt=0.0)
    max_retries: int = Field(default=2, ge=0)
    model_config_path: Path = DEFAULT_MODEL_CONFIG_PATH
    provider_config_dir: Path = DEFAULT_PROVIDER_CONFIG_DIR
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    openai: OpenAIProviderConfig = Field(default_factory=OpenAIProviderConfig)
    anthropic: PlaceholderProviderConfig = Field(default_factory=PlaceholderProviderConfig)
    gemini: PlaceholderProviderConfig = Field(default_factory=PlaceholderProviderConfig)
    local: LocalProviderConfig = Field(default_factory=LocalProviderConfig)

    @model_validator(mode="after")
    def set_embedding_provider_default(self) -> "AppConfig":
        if self.embedding_provider is None:
            self.embedding_provider = self.model_provider
        return self

    def load_provider_preset(self, provider_name: ProviderName) -> ProviderPreset:
        """Load a provider preset from configs/providers when present."""

        preset_path = self.provider_config_dir / f"{provider_name}.toml"
        if not preset_path.exists():
            return ProviderPreset(provider_name=provider_name)
        return ProviderPreset.model_validate(_load_toml(preset_path))

    def _provider_api_key(self, provider_name: ProviderName) -> SecretStr | None:
        if provider_name == "openai":
            return SecretStr(self.openai.api_key) if self.openai.api_key else None
        if provider_name == "anthropic":
            return SecretStr(self.anthropic.api_key) if self.anthropic.api_key else None
        if provider_name == "gemini":
            return SecretStr(self.gemini.api_key) if self.gemini.api_key else None
        return None

    def resolve_chat_provider(self) -> ResolvedProviderConfig:
        """Resolve the chat provider using preset defaults plus env overrides."""

        preset = self.load_provider_preset(self.model_provider)
        if self.model_provider == "local":
            chat_model = self.local.chat_model
            embedding_model = self.local.embedding_model
            base_url = None
            timeout_seconds = min(self.request_timeout_seconds, preset.timeout_seconds)
            max_retries = min(self.max_retries, preset.max_retries)
        elif self.model_provider == "openai":
            chat_model = self.chat_model or preset.default_chat_model or "gpt-4.1-mini"
            embedding_model = self.embedding_model or preset.default_embedding_model or "text-embedding-3-small"
            base_url = self.openai.base_url or preset.base_url
            timeout_seconds = self.request_timeout_seconds
            max_retries = self.max_retries
        else:
            chat_model = self.chat_model or preset.default_chat_model or "not-implemented"
            embedding_model = self.embedding_model or preset.default_embedding_model or "not-implemented"
            provider_section = self.anthropic if self.model_provider == "anthropic" else self.gemini
            base_url = provider_section.api_base or preset.base_url
            timeout_seconds = self.request_timeout_seconds
            max_retries = self.max_retries

        return ResolvedProviderConfig(
            provider_name=self.model_provider,
            chat_model=chat_model,
            embedding_model=embedding_model,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            routing_strategy=self.routing.strategy,
            embedding_dimension=self.local.embedding_dimensions,
            response_prefix=self.local.response_prefix,
            api_key=self._provider_api_key(self.model_provider),
        )

    def resolve_embedding_provider(self) -> ResolvedProviderConfig:
        """Resolve the embedding provider using preset defaults plus env overrides."""

        provider_name = self.embedding_provider or self.model_provider
        preset = self.load_provider_preset(provider_name)

        if provider_name == "local":
            return ResolvedProviderConfig(
                provider_name=provider_name,
                chat_model=self.local.chat_model,
                embedding_model=self.local.embedding_model,
                base_url=None,
                timeout_seconds=min(self.request_timeout_seconds, preset.timeout_seconds),
                max_retries=min(self.max_retries, preset.max_retries),
                routing_strategy=self.routing.strategy,
                embedding_dimension=self.local.embedding_dimensions,
                response_prefix=self.local.response_prefix,
                api_key=None,
            )

        if provider_name == "openai":
            return ResolvedProviderConfig(
                provider_name=provider_name,
                chat_model=self.chat_model or preset.default_chat_model or "gpt-4.1-mini",
                embedding_model=self.embedding_model or preset.default_embedding_model or "text-embedding-3-small",
                base_url=self.openai.base_url or preset.base_url,
                timeout_seconds=self.request_timeout_seconds,
                max_retries=self.max_retries,
                routing_strategy=self.routing.strategy,
                embedding_dimension=preset.embedding_dimension or self.local.embedding_dimensions,
                response_prefix=self.local.response_prefix,
                api_key=self._provider_api_key(provider_name),
            )

        provider_section = self.anthropic if provider_name == "anthropic" else self.gemini
        return ResolvedProviderConfig(
            provider_name=provider_name,
            chat_model=self.chat_model or preset.default_chat_model or "not-implemented",
            embedding_model=self.embedding_model or preset.default_embedding_model or "not-implemented",
            base_url=provider_section.api_base or preset.base_url,
            timeout_seconds=self.request_timeout_seconds,
            max_retries=self.max_retries,
            routing_strategy=self.routing.strategy,
            embedding_dimension=preset.embedding_dimension or self.local.embedding_dimensions,
            response_prefix=self.local.response_prefix,
            api_key=self._provider_api_key(provider_name),
        )


class EnvironmentOverrides(BaseSettings):
    """Environment-driven runtime overrides.

    All `RIA_` values are optional and override the selected TOML preset when set.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="RIA_",
        extra="ignore",
    )

    model_config_path: str | None = None
    provider_config_dir: str | None = None
    model_provider: ProviderName | None = None
    embedding_provider: ProviderName | None = None
    chat_model: str | None = None
    embedding_model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    request_timeout_seconds: float | None = None
    max_retries: int | None = None
    routing_strategy: RoutingStrategy | None = None
    routing_enable_fallback: bool | None = None
    routing_fallback_order: str | None = None
    openai_base_url: str | None = None
    openai_organization: str | None = None
    openai_project: str | None = None
    local_chat_model: str | None = None
    local_embedding_model: str | None = None
    local_embedding_dimensions: int | None = None
    local_response_prefix: str | None = None
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, validation_alias="GOOGLE_API_KEY")


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def _resolve_model_config_path(path_value: str | Path | None) -> Path:
    if path_value is None:
        return DEFAULT_MODEL_CONFIG_PATH

    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _build_env_override_dict(env: EnvironmentOverrides) -> dict[str, Any]:
    data: dict[str, Any] = {}

    simple_fields = (
        "model_provider",
        "embedding_provider",
        "chat_model",
        "embedding_model",
        "temperature",
        "max_tokens",
        "request_timeout_seconds",
        "max_retries",
    )

    for field_name in simple_fields:
        value = getattr(env, field_name)
        if value is not None:
            data[field_name] = value

    if env.provider_config_dir is not None:
        data["provider_config_dir"] = _resolve_model_config_path(env.provider_config_dir)

    routing: dict[str, Any] = {}
    if env.routing_strategy is not None:
        routing["strategy"] = env.routing_strategy
    if env.routing_enable_fallback is not None:
        routing["enable_fallback"] = env.routing_enable_fallback
    if env.routing_fallback_order:
        routing["fallback_order"] = [item.strip() for item in env.routing_fallback_order.split(",") if item.strip()]
    if routing:
        data["routing"] = routing

    openai: dict[str, Any] = {}
    if env.openai_api_key is not None:
        openai["api_key"] = env.openai_api_key
    if env.openai_base_url is not None:
        openai["base_url"] = env.openai_base_url
    if env.openai_organization is not None:
        openai["organization"] = env.openai_organization
    if env.openai_project is not None:
        openai["project"] = env.openai_project
    if openai:
        data["openai"] = openai

    anthropic: dict[str, Any] = {}
    if env.anthropic_api_key is not None:
        anthropic["api_key"] = env.anthropic_api_key
    if anthropic:
        data["anthropic"] = anthropic

    gemini: dict[str, Any] = {}
    if env.google_api_key is not None:
        gemini["api_key"] = env.google_api_key
    if gemini:
        data["gemini"] = gemini

    local: dict[str, Any] = {}
    if env.local_chat_model is not None:
        local["chat_model"] = env.local_chat_model
    if env.local_embedding_model is not None:
        local["embedding_model"] = env.local_embedding_model
    if env.local_embedding_dimensions is not None:
        local["embedding_dimensions"] = env.local_embedding_dimensions
    if env.local_response_prefix is not None:
        local["response_prefix"] = env.local_response_prefix
    if local:
        data["local"] = local

    return data


@lru_cache(maxsize=8)
def load_settings(config_path: str | Path | None = None) -> AppConfig:
    """Load app settings from TOML plus environment overrides."""

    env = EnvironmentOverrides()
    resolved_path = _resolve_model_config_path(config_path or env.model_config_path)
    merged = _deep_merge(_load_toml(resolved_path), _build_env_override_dict(env))
    merged["model_config_path"] = resolved_path
    return AppConfig.model_validate(merged)


def get_settings(config_path: str | Path | None = None) -> AppConfig:
    """Compatibility alias for the cached settings loader."""

    return load_settings(config_path)