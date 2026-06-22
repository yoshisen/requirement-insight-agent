# rag/grounding

retrieval の結果を synthetic agent 実行向けの grounding context に変換する層です。

- retrieved chunk の束を `GroundingContext` に変換
- 根拠不足時は `overall_uncertainty` を引き上げる
- citation trace を保持したまま後段へ渡す