# Roadmap

この文書は README のロードマップを、実装着手しやすい単位へ落とし込んだものです。
現時点では **MVP 前提 / Spec-first** を維持し、まずは end-to-end の最小パスを作ることを優先します。

## Current Focus

- Current phase: `Phase 0 -> Phase 1 bridge`
- Goal: 仕様だけの状態から、最小限の scaffold と schema-first 実装基盤へ移行する
- Success criteria:
  - Python プロジェクトとして起動できる
  - 主要 schema が JSON Schema として存在する
  - docs / configs / examples / tests の最小配置がある
  - 安全性とデータ利用ポリシーが明文化されている

## Phase 0: Spec / README / Architecture

- README を OSS ホームとして整理する
- アーキテクチャ設計を文書化する
- 安全・非目標・ライセンス方針を明文化する

## Phase 1: Data / Schema / Simple Personas

- `schemas/` に MVP schema を定義する
- `data/sample/` に安全な sample assets の置き場所を作る
- `configs/` に最小 scenario / provider 設定方針を置く
- synthetic agent の最小例を扱える validation path を作る

## Phase 2: RAG + Agent Orchestration

- 文書 chunking と retrieval の最小実装を作る
- grounding context bundle のフォーマットを固定する
- 単一 scenario に対する per-agent 実行パスを作る
- citation trace を保持できるようにする

## Phase 3: Aggregation / Reporting

- segment summary の最小集約ロジックを作る
- objections / reasons / channel preference を集約する
- uncertainty summary と explanation trace の出力形式を定義する

## Phase 4: Scenario Simulation / Demand Range

- price / channel / positioning variant を比較可能にする
- conservative / base / optimistic の range 出力を追加する
- inventory suggestion を deterministic ではなく range で返す

## Phase 5: Calibration / Evaluation

- representativeness checks を追加する
- run-to-run stability の確認手順を追加する
- optional benchmark / real survey comparison の接点を作る

## Phase 6: API / UI / Multi-region

- Minimal API を追加する
- CLI から API への責務分離を進める
- 地域拡張のための config / schema 差分を整理する

## Immediate Next Milestones

1. Pydantic v2 models を `schemas/` と 1:1 で対応させる
2. scenario 読み込みと schema validation の CLI コマンドを追加する
3. sample scenario を使った dummy end-to-end execution を追加する