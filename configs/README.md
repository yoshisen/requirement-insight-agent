# configs

このディレクトリは、非 secret の設定ファイル置き場です。
MVP では主に以下を想定します。

- model provider defaults
- provider-specific runtime presets
- pipeline presets
- scenario presets

命名は `kebab-case` または `snake_case` で統一し、設定 ID は `tokyo-mvp-v1` のように version を含めます。