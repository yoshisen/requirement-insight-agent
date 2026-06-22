# data/processed

正規化後のデータ、中間テーブル、index 入力用の artifact を置く場所です。

- schema-aware に変換する
- source metadata を失わない
- 再生成可能なものはコードで再作成できる形を優先する

MVP の ingestion CLI は、既定で `data/processed/normalized_records.json` をここに出力します。