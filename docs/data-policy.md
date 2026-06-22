# Data Policy

## 目的

この文書は、README と architecture で定義したデータ利用原則を、実務上の repository ルールへ落とし込むためのものです。

## 必須メタデータ

各データセットには、最低限以下を持たせます。

- `datasource_id`
- `source_name`
- `source_type`
- `license_type`
- `allowed_use`
- `retrieved_at`
- `coverage_region`
- `quality_score`
- `provenance`

## 保存ルール

- 未加工データは `data/raw/` に置く
- 正規化済み・派生データは `data/processed/` に置く
- 再配布可能な最小例は `data/sample/` に置く
- secret や API キーは `.env` にのみ置き、Git 管理しない

## 利用制約

- 違法な scraping を前提にしない
- 個人再構成につながるデータを扱わない
- 公開アクセス可能であることを自由利用可能と同一視しない
- provenance 不明のデータを MVP の根拠に使わない