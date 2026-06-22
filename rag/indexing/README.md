# rag/indexing

RAG 用のローカル index を作る層です。

- `chunker.py`: 正規化済み ingestion record を chunk 化する
- `build.py`: chunk を embedding して local index bundle を保存する

出力物:

- `manifest.json`
- `metadata.json`
- `vectors.npy`
- `index.faiss`（FAISS 利用可能時）