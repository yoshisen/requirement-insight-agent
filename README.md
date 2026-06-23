# Requirement Insight Agent

[![Repository](https://img.shields.io/badge/GitHub-yoshisen%2Frequirement--insight--agent-181717?logo=github)](https://github.com/yoshisen/requirement-insight-agent)
[![Branch](https://img.shields.io/badge/branch-main-0A66C2)](https://github.com/yoshisen/requirement-insight-agent/tree/main)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Status](https://img.shields.io/badge/status-MVP%20pipeline%20implemented-green)](https://github.com/yoshisen/requirement-insight-agent)

> **会話から要件へ。**
>
> Requirement Insight Agent は、公開データ、RAG、population-aligned synthetic consumer agents を組み合わせて、
> 市場要求の探索、需要仮説の形成、シナリオ評価、意思決定支援を行うための OSS です。

## このプロジェクトの核心

Requirement Insight Agent の核心は、**現実にできるだけ近い synthetic consumer agents を構築し、
商品・価格・訴求・販路・地域条件に対する需要反応をシミュレーションすること** にあります。

これは「何が売れるか」を単純に断定する仕組みではなく、
**どの市場で、どの層が、どの条件で反応しそうか** を比較可能な形で可視化し、
意思決定者が実調査前に論点整理、仮説比較、施策検討を行うための reference workflow を提供するものです。

この agent は、公開データだけでなく、**適法で、利用許諾があり、監査可能な社内データ、調査メモ、商品情報、地域情報** なども取り込みながら構成できます。
目標は、実在個人を再構成することではなく、対象市場に整合する synthetic population を作り、
できる限り現実に近い反応分布を再現して、需要理解と意思決定支援に役立てることです。

このプロジェクトが目指しているのは、「何が売れるか」を単純に当てることではなく、
**どの市場で、どの層に、どの価値提案が、どの条件つきで受け入れられそうか** を、
構造化された simulation workflow として検討できるようにすることです。

市場調査の現場では、最初から十分な実データ、十分なインタビュー対象、十分な予算、十分に磨かれた仮説がそろっているとは限りません。
Requirement Insight Agent は、そうした初期段階の不確実な問いに対して、
公開データ、地域情報、カテゴリ知識、retrieval、synthetic consumer agents を組み合わせ、
**仮説生成、事前比較、論点整理、需要レンジの探索** を支援することを目的にしています。

重要なのは、このプロジェクトが **real market research の代替** ではないことです。
ここで生成される結果は、forecast や business truth ではなく、
**grounded but uncertain simulation output** として扱われるべきものです。
そのため、どの出力にも、できる限り assumptions、citations、uncertainty、explanation trace を残す方針をとっています。

## このプロジェクトの目的

- 市場要求や潜在ニーズを、定性的な会話と定量寄りの構造出力の両方で探索できるようにする
- 商品、価格、地域、訴求、チャネルの違いを scenario として比較できるようにする
- synthetic population を使って、平均的な 1 人の顧客像ではなく、分布としての反応差を扱えるようにする
- calibration 可能な形で、後から benchmark や real-world data と比較できる実装基盤を作る
- OSS として、schema、config、ingestion、RAG、runner、aggregation、estimation、evaluation を段階的に拡張できるようにする

## 実現方法

現在の実装は、以下の流れで構成されています。

1. `ingestion`
  local の CSV / JSON / Markdown / text と datasource metadata を読み込み、provenance-aware な正規化データへ変換します。

2. `RAG`
  正規化済みデータを chunk 化し、embedding を作り、FAISS 優先の local index に保存します。
  retrieval 時には region / category / datasource metadata で絞り込み、citation trace を保持します。

3. `synthetic population`
  weighted config に基づいて、region、household、age band、income band、channel preference、price sensitivity などを持つ synthetic agents を複数生成します。
  raw traits と derived traits を分けて保持し、将来の calibration をしやすくしています。

4. `survey / interview runner`
  scenario、agent profile、grounding context、prompt spec を結びつけて、structured JSON response を返します。
  local provider でも OpenAI でも、同じ request / response contract を通す構造です。

5. `aggregation / scoring`
  per-agent response をセグメント別・全体で集約し、top reasons、top objections、purchase intent distribution、channel preference summary、uncertainty summary を出します。

6. `demand estimation / inventory suggestion`
  aggregated output をもとに、conservative / base / optimistic の range を推定し、inventory suggestion を range として返します。

7. `evaluation / calibration`
  expected distribution や benchmark と比較して、representativeness、stability、evidence coverage、bias risk を確認します。

## 最短の使い方

最短で sample flow を試すなら、次の順で十分です。

1. `ria ingest`
2. `ria build-index --input data/processed/normalized_records.json --output-dir .local/index/sample`
3. `ria build-population --config configs/populations/tokyo_mvp_population.json --sample-size 24 --category frozen_food --output agents/sample_profiles/tokyo_mvp_population.sample.json`
4. `ria run-scenario --scenario examples/tokyo-supermarket-launch/scenario.json --prompt prompts/survey/supermarket-launch-survey-v1.json --population agents/sample_profiles/tokyo_mvp_population.sample.json --index-dir .local/index/sample --agent-limit 5 --output .local/output/scenario_run.json --jsonl-output .local/output/scenario_run.jsonl`
5. `ria aggregate --run-result .local/output/scenario_run.json --population agents/sample_profiles/tokyo_mvp_population.sample.json --output .local/output/aggregated_output.json --report .local/output/aggregation_report.md`
6. `ria estimate-demand --aggregation .local/output/aggregated_output.json --base-units 900 --output .local/output/demand_estimation.json --report .local/output/demand_estimation_report.md`
7. `ria evaluate --population agents/sample_profiles/tokyo_mvp_population.sample.json --aggregation .local/output/aggregated_output.json --benchmark evaluation/benchmarks/tokyo_mvp_expected_distribution.json --output .local/output/evaluation_record.json --report .local/output/evaluation_report.md`

もっと早く end-to-end を確認したい場合は、以下の 1 コマンドで sample workflow をまとめて実行できます。

```bash
ria run-example \
  --config examples/tokyo-supermarket-launch/example_config.json \
  --prompt-kind survey \
  --agent-limit 5 \
  --base-units 900 \
  --output-dir .local/examples/tokyo-supermarket-launch
```

生成される主な成果物は以下です。

- `normalized_records.json`
- `scenario_run.json`
- `aggregated_output.json`
- `aggregation_report.md`
- `demand_estimation.json`
- `demand_estimation_report.md`
- `evaluation_record.json`
- `evaluation_report.md`

詳細なコマンドとファイル説明は、この README の下部セクション、および [docs/getting-started.md](docs/getting-started.md) と [docs/runbook.md](docs/runbook.md) にまとめています。

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