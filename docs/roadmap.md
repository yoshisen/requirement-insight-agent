# Roadmap

この文書は README のロードマップを、実装着手しやすい単位へ落とし込んだものです。
現時点では **MVP 前提 / Spec-first** を維持し、まずは end-to-end の最小パスを作ることを優先します。

## Current Focus

- Current phase: `Phase 5 -> Phase 6 bridge`
- Goal: 既存の MVP pipeline を calibration / evaluation / API / docs まで通し、end-to-end の再現可能性を高める
- Success criteria:
  - sample flow が `ingest -> build-index -> build-population -> run-scenario -> aggregate -> estimate-demand -> evaluate` で通る
  - local / OpenAI provider の切替方法が明文化されている
  - minimal API から sample flow を叩ける
  - README / getting-started / runbook が現実装と整合する

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

1. stronger calibration against real survey or benchmark data
2. provider expansion beyond local / OpenAI placeholder mix
3. richer scenario coverage and more stable reporting