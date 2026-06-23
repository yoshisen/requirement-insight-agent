from requirement_insight_agent.core.config import AppConfig, load_settings
from requirement_insight_agent.core.providers.exceptions import ProviderAuthenticationError
from requirement_insight_agent.core.providers.factory import create_provider_stack
from requirement_insight_agent.core.providers.models import ChatMessage, ChatRequest, EmbeddingRequest


def test_local_provider_stack_smoke() -> None:
    settings = AppConfig(
        model_provider="local",
        embedding_provider="local",
        local={
            "chat_model": "local-placeholder-chat",
            "embedding_model": "local-placeholder-embedding",
            "embedding_dimensions": 12,
            "response_prefix": "[local-test]",
        },
    )
    stack = create_provider_stack(settings)

    chat_response = stack.chat.complete(
        ChatRequest(messages=[ChatMessage(role="user", content="Summarize the scenario")])
    )
    embedding_response = stack.embeddings.embed(EmbeddingRequest(texts=["alpha", "beta"]))

    assert chat_response.provider == "local"
    assert "Summarize the scenario" in chat_response.output_text
    assert len(embedding_response.vectors) == 2
    assert len(embedding_response.vectors[0].values) == 12


def test_openai_provider_requires_api_key() -> None:
    settings = AppConfig(model_provider="openai", embedding_provider="openai")
    stack = create_provider_stack(settings)

    try:
        stack.chat.complete(ChatRequest(messages=[ChatMessage(role="user", content="Hello")]))
        raise AssertionError("Expected ProviderAuthenticationError")
    except ProviderAuthenticationError:
        pass


def test_app_config_resolves_embedding_provider() -> None:
    settings = AppConfig(model_provider="local", embedding_provider="local")

    embedding_config = settings.resolve_embedding_provider()

    assert embedding_config.provider_name == "local"
    assert embedding_config.embedding_dimension == 8


def test_load_settings_respects_env_provider_selection(monkeypatch) -> None:
    load_settings.cache_clear()
    monkeypatch.setenv("RIA_MODEL_PROVIDER", "local")
    monkeypatch.setenv("RIA_EMBEDDING_PROVIDER", "local")

    settings = load_settings()

    assert settings.model_provider == "local"
    assert settings.embedding_provider == "local"

    load_settings.cache_clear()