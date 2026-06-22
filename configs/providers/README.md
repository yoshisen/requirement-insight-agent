# configs/providers

provider 固有の設定プリセットを置くディレクトリです。

- `openai.toml`: OpenAI の既定値
- `anthropic.toml`: Claude 系 provider の既定値
- `gemini.toml`: Gemini 系 provider の既定値
- `local.toml`: local placeholder provider の既定値

MVP では env 変数が最優先で、これらの preset は初期値や共有テンプレートとして扱います。