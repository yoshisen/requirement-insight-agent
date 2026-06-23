# Requirement Insight Agent

[![Repository](https://img.shields.io/badge/GitHub-yoshisen%2Frequirement--insight--agent-181717?logo=github)](https://github.com/yoshisen/requirement-insight-agent)
[![Branch](https://img.shields.io/badge/branch-main-0A66C2)](https://github.com/yoshisen/requirement-insight-agent/tree/main)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Status](https://img.shields.io/badge/status-MVP%20pipeline%20implemented-green)](https://github.com/yoshisen/requirement-insight-agent)

> **会話から要件へ。**
>
> Requirement Insight Agent は、公開データ、RAG、population-aligned synthetic consumer agents を組み合わせて、
> 市場要求の探索、需要仮説の形成、シナリオ評価、意思決定支援を行うための OSS です。

## 現在実装済みの範囲

- schema-first な JSON Schema / Pydantic models
- provider abstraction と local / OpenAI 切替基盤
- local CSV / JSON / Markdown / text ingestion
- FAISS 優先の local RAG index / retrieval / grounding
- weighted config ベースの synthetic population generation
- survey / interview runner
- aggregation / scoring / markdown reporting
- demand estimation / inventory suggestion
- evaluation / calibration MVP
- Typer CLI と FastAPI 最小 API
- 東京圏スーパー新商品上市の sample flow

## まだ未実装の範囲

- 実データ連携を前提にした強い calibration
- provider ごとの本格的な production 実装（Claude / Gemini）
- 高度な geospatial reasoning
- 非同期 job orchestration
- 本格 UI
- 継続運用を前提にした benchmark / backtest の蓄積

## リポジトリの目的

このプロジェクトは市場を deterministic に予測するものではありません。
目標は、以下を構造化された workflow として OSS 化することです。

- 仮説生成
- pre-evaluation
- scenario comparison
- uncertainty-aware reporting
- calibration-ready evaluation

## インストール方法

### 前提

- Python 3.11+
- 推奨: virtual environment

### セットアップ

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev,rag]
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev,rag]
```

## `.env` 設定方法

```bash
cp .env.example .env
```

主要設定:

- `RIA_MODEL_PROVIDER`
- `RIA_EMBEDDING_PROVIDER`
- `RIA_CHAT_MODEL`
- `RIA_EMBEDDING_MODEL`
- `OPENAI_API_KEY`
- `RIA_MODEL_CONFIG_PATH`

## OpenAI / local model の切替方法

### local placeholder

```env
RIA_MODEL_PROVIDER=local
RIA_EMBEDDING_PROVIDER=local
RIA_CHAT_MODEL=local-placeholder-chat
RIA_EMBEDDING_MODEL=local-placeholder-embedding
```

### OpenAI

```env
RIA_MODEL_PROVIDER=openai
RIA_EMBEDDING_PROVIDER=openai
RIA_CHAT_MODEL=gpt-4.1-mini
RIA_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-key
```

## sample data の使い方

sample assets は `data/sample/` にあります。

- `tokyo_regions.csv`
- `tokyo_products.json`
- `tokyo_market_notes.md`
- `tokyo_quick_notes.txt`
- `datasource_manifest.json`

## RAG index 作成方法

```bash
ria ingest
ria build-index --input data/processed/normalized_records.json --output-dir .local/index/sample
ria retrieve-test --index-dir .local/index/sample --query-file examples/tokyo-supermarket-launch/retrieval_query.json --output .local/output/retrieval_result.json
```

## synthetic population 作成方法

```bash
ria build-population \
  --config configs/populations/tokyo_mvp_population.json \
  --sample-size 24 \
  --category frozen_food \
  --output agents/sample_profiles/tokyo_mvp_population.sample.json
```

## example scenario 実行方法

### 個別に流す場合

```bash
ria run-scenario \
  --scenario examples/tokyo-supermarket-launch/scenario.json \
  --prompt prompts/survey/supermarket-launch-survey-v1.json \
  --population agents/sample_profiles/tokyo_mvp_population.sample.json \
  --index-dir .local/index/sample \
  --agent-limit 5 \
  --output .local/output/scenario_run.json \
  --jsonl-output .local/output/scenario_run.jsonl

ria aggregate \
  --run-result .local/output/scenario_run.json \
  --population agents/sample_profiles/tokyo_mvp_population.sample.json \
  --output .local/output/aggregated_output.json \
  --report .local/output/aggregation_report.md

ria estimate-demand \
  --aggregation .local/output/aggregated_output.json \
  --base-units 900 \
  --output .local/output/demand_estimation.json \
  --report .local/output/demand_estimation_report.md

ria evaluate \
  --population agents/sample_profiles/tokyo_mvp_population.sample.json \
  --aggregation .local/output/aggregated_output.json \
  --benchmark evaluation/benchmarks/tokyo_mvp_expected_distribution.json \
  --output .local/output/evaluation_record.json \
  --report .local/output/evaluation_report.md
```

### end-to-end sample flow

```bash
ria run-example \
  --config examples/tokyo-supermarket-launch/example_config.json \
  --prompt-kind survey \
  --agent-limit 5 \
  --base-units 900 \
  --output-dir .local/examples/tokyo-supermarket-launch
```

## 出力の見方

主な成果物:

- `normalized_records.json`
- `retrieval_result.json`
- `population.json`
- `scenario_run.json`
- `scenario_run.jsonl`
- `aggregated_output.json`
- `aggregation_report.md`
- `demand_estimation.json`
- `demand_estimation_report.md`
- `evaluation_record.json`
- `evaluation_report.md`

解釈上の注意:

- `aggregation_report.md` は hypothesis-support 用の summary
- `demand_estimation.json` は scenario-based range であり、forecast ではない
- `evaluation_record.json` は current calibration gap を残すための scaffold

## API

起動:

```bash
python -m uvicorn api.app:app --reload
```

主な endpoint:

- `GET /health`
- `POST /population/build`
- `POST /scenario/run`
- `POST /examples/tokyo-supermarket-launch/run`
- `GET /results/{artifact_name}`

## CLI コマンド一覧

- `ria status`
- `ria paths`
- `ria ingest`
- `ria build-index`
- `ria retrieve-test`
- `ria build-population`
- `ria run-scenario`
- `ria aggregate`
- `ria estimate-demand`
- `ria evaluate`
- `ria run-example`

## 倫理・安全・非目標

- synthetic agents は実在人物ではない
- 実在個人の再構成・模倣・プロファイリングを目的としない
- 違法・不透明な scraping を前提にしない
- 結果は deterministic truth ではなく structured simulation result として扱う
- 高リスクな投資判断をこの出力単独で行わない

詳細は以下を参照してください。

- [docs/safety.md](docs/safety.md)
- [docs/data-policy.md](docs/data-policy.md)

## limitation

- local provider は placeholder 実装
- Claude / Gemini は abstraction のみで本実装は未完了
- calibration は benchmark scaffold 段階
- RAG は local index MVP に留まる
- aggregation / demand estimation は deterministic heuristic ベース
- report の品質は real-world validation に依存する

## roadmap の更新

現状の実装位置づけ:

- Phase 0-4: MVP 実装済み
- Phase 5: evaluation / calibration の土台実装済み
- Phase 6: minimal API 実装済み

次の優先事項:

1. stronger calibration against real benchmarks
2. richer example coverage
3. provider expansion beyond local / OpenAI
4. end-to-end CLI polish and error messaging

## 参考ドキュメント

- [docs/getting-started.md](docs/getting-started.md)
- [docs/runbook.md](docs/runbook.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/schema-spec.md](docs/schema-spec.md)
- [docs/roadmap.md](docs/roadmap.md)

## License

Apache License 2.0