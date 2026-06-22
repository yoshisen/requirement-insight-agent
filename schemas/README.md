# schemas

このディレクトリには、MVP 実装で使う JSON Schema を置きます。

- `agent.schema.json`: synthetic consumer agent
- `datasource.schema.json`: data source metadata
- `scenario.schema.json`: scenario input
- `output.schema.json`: aggregated output + demand estimation bundle
- `evaluation.schema.json`: evaluation / calibration record

## Validation Policy

- 必須フィールドは `docs/schema-spec.md` の MVP 要件に合わせる
- `additionalProperties: false` を基本とし、想定外の personal identity field を受け入れにくくする
- `license_type`、`allowed_use`、`provenance` を data source で必須にする
- `uncertainty`、`citation`、`explanation trace` を output / evaluation 系に含める
- sample JSON は `schemas/examples/` に置き、テストで validation を通す

将来的には Pydantic v2 models と 1:1 で対応させます。