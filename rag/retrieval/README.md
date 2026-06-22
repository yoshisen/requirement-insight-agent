# rag/retrieval

ローカル index bundle から chunk を検索する層です。

- region / category / datasource filter
- FAISS 優先、未導入時は numpy fallback
- citation metadata 付き `RetrievedChunk` を返す