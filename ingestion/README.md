# ingestion

外部データの読込と初期整形の責務を持つディレクトリです。

MVP では以下の流れを想定します。

- source file を読む
- basic metadata を付与する
- normalized record へ渡せる形にする
- local CSV / JSON / Markdown / text を扱う
- provenance と license を record に残す
- `data/processed/normalized_records.json` を生成する

将来的には public statistics、geospatial、retail、survey などの connector をここに追加します。

## 現在の主要ファイル

- `models.py`: manifest と normalized output のモデル
- `loaders.py`: CSV / JSON / Markdown / text loader
- `pipeline.py`: manifest 読込、正規化、保存

## Normalized Format

出力の 1 レコードは最低限以下を持ちます。

- `record_id`
- `datasource_id`
- `source_name`
- `source_type`
- `source_path`
- `content_format`
- `title`
- `text`
- `structured_data`
- `coverage_region`
- `license_type`
- `allowed_use`
- `quality_score`
- `provenance`
- `normalized_at`