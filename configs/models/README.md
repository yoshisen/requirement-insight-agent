# configs/models

モデルプロバイダや埋め込みモデルの既定設定を置く場所です。

- provider
- embedding provider
- chat model
- embedding model
- temperature
- retry policy

MVP では以下の preset を提供します。

- `default.toml`: ローカル placeholder を既定にした安全な開発用設定
- `openai.toml`: OpenAI を chat / embedding の両方に使う想定設定
- `local.toml`: 完全ローカル placeholder で smoke test する設定
- `claude.toml`: 将来実装用の placeholder 設定
- `gemini.toml`: 将来実装用の placeholder 設定