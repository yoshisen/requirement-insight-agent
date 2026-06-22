# Evaluation

## MVP で評価すること

MVP の段階では、予測精度そのものよりも、構造化・再現性・安全性が成立しているかを重視します。

## 初期評価軸

- schema validation が通るか
- synthetic population が target assumptions と大きく矛盾していないか
- retrieval が scenario に関係する evidence を返しているか
- 同一 config / seed で極端に不安定な出力にならないか
- summary と demand range に uncertainty が明示されているか

## 初期チェック例

- sample payload を JSON Schema / Pydantic model の両方で検証する
- population config と生成結果の比率を比較する
- scenario output に citation trace が含まれるか確認する
- single-point prediction ではなく range 出力になっているか確認する