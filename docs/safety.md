# Safety

## 目的

この文書は、Requirement Insight Agent における倫理・安全性・プライバシー・非目標を、
実装者とコントリビュータが参照しやすい運用ガイドとしてまとめたものです。

## 基本方針

- 本システムは研究・仮説生成・意思決定支援のための OSS である
- synthetic consumer agents は実在個人ではない
- 出力は deterministic truth ではなく scenario-based insight with uncertainty として扱う
- すべてのデータ利用は適法・監査可能・ライセンス準拠でなければならない
- 人間によるレビューと最終判断を前提とする

## 非目標

- 実市場調査の完全代替
- 保証された需要予測
- 実在個人の再構成・模倣・プロファイリング
- 政治的説得や世論操作
- 脆弱な層のターゲティングや搾取
- 違法または不透明なスクレイピング基盤の提供

## 禁止事項

- 実名、個人識別子、SNS アカウント単位の profile を生成・保存しない
- センシティブ属性を有害な最適化対象にしない
- 出所や利用許諾が不明なデータを正当化しない
- 断定できない内容を確実な事実として出力しない

## データ利用ルール

- raw data は `data/raw/` に置く前に利用条件を確認する
- `allowed_use` と `license_type` を必ず残す
- sample data は再配布可能で安全なものに限定する
- 個人再構成につながるデータはリポジトリに含めない

## 出力ルール

- demand / inventory は single-point prediction ではなく range で表現する
- 可能な限り citation / provenance / uncertainty を残す
- 説明不能な推定や推論飛躍は uncertainty を上げて扱う

## Contributor Checklist

- その変更は README / architecture / schema-spec と矛盾していないか
- 新しいデータ項目は safety-aware か
- schema / docs / sample / tests のどれを同時更新すべきか確認したか
- 実装が人間レビュー前提であることを壊していないか