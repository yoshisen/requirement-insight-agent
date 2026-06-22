# rag

RAG 関連の実装を置くディレクトリです。

- indexing
- retrieval
- grounding context assembly
- citation trace generation

MVP では、まず region / category / scenario 条件で絞れる retrieval path を目指します。

## Current MVP Structure

- `indexing/`: chunking と local index bundle 生成
- `retrieval/`: query, filter, hybrid retrieval
- `grounding/`: `GroundingContext` builder

## Local Index Bundle

`build-index` 実行後、既定で `.local/index/sample/` に以下を生成します。

- `manifest.json`
- `metadata.json`
- `vectors.npy`
- `index.faiss`（FAISS が利用可能な場合）