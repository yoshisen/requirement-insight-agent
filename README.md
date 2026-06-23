# Requirement Insight Agent

[![Repository](https://img.shields.io/badge/GitHub-yoshisen%2Frequirement--insight--agent-181717?logo=github)](https://github.com/yoshisen/requirement-insight-agent)
[![Branch](https://img.shields.io/badge/branch-main-0A66C2)](https://github.com/yoshisen/requirement-insight-agent/tree/main)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Status](https://img.shields.io/badge/status-MVP%20pipeline%20implemented-green)](https://github.com/yoshisen/requirement-insight-agent)

> **会話から要件へ。**
>
> Requirement Insight Agent は、公開データや許諾済みデータをもとに synthetic consumer agents を構築し、
> 商品・価格・訴求・販路・地域条件に対する需要反応を、できる限り現実に近いかたちでシミュレーションするための OSS です。

## このプロジェクトの核心

このプロジェクトの一番の価値は、**合成エージェントを使って、現実の市場に近い需要反応を事前に比較できること** にあります。

単に「売れる / 売れない」を断定するのではなく、次のような問いに対して、比較しやすいかたちで反応を出します。

- どの層が反応しそうか
- どの価格帯で失速しそうか
- どの訴求が効きやすいか
- どの販路や地域条件で受け止められ方が変わるか

そのために、公開統計、地域情報、商品情報、調査メモ、社内の許諾済みデータなどを取り込み、
対象市場にできるだけ整合する synthetic population を作り、その上でシナリオ実行、集約、需要レンジ推定、評価までを一つの流れとして扱います。

このプロジェクトは **実市場調査の代替** ではありません。
出力はあくまで **仮説生成・比較検討・論点整理・意思決定支援** のための simulation result です。

## まず分かること

この README を読むと、最低限次のことが分かります。

- このプロジェクトが何を目指しているか
- 何を入力にして synthetic agents を作るのか
- OpenAI や local mode をどこで設定するのか
- CLI をどういう順番で実行すればよいか
- 実行すると何が出力されるのか
- どこまで実装済みで、どこが未実装か

## 目次

- [1. 何をするプロジェクトか](#1-何をするプロジェクトか)
- [2. 現在できること](#2-現在できること)
- [3. まだ未実装のこと](#3-まだ未実装のこと)
- [4. どう実現しているか](#4-どう実現しているか)
- [5. 設定はどこでするか](#5-設定はどこでするか)
- [6. 最短の使い方](#6-最短の使い方)
- [7. 実行すると何が出るか](#7-実行すると何が出るか)
- [8. CLI と API](#8-cli-と-api)
- [9. 倫理・安全・制約](#9-倫理安全制約)
- [10. 関連ドキュメント](#10-関連ドキュメント)

## 1. 何をするプロジェクトか

Requirement Insight Agent は、次の流れを OSS として実装することを目標にしています。

1. 市場理解に使えるデータを取り込む
2. それを RAG 可能な知識ベースにする
3. 分布ベースで synthetic consumer agents を生成する
4. 商品や施策のシナリオを agent に投げる
5. 応答を集約して、需要や懸念点を整理する
6. conservative / base / optimistic の range を出す
7. benchmark と比較して未校正点を明示する

対象は冷凍惣菜のような新商品だけに限りません。
価格施策、販促、棚割り、チャネル、出店仮説、サービス構想など、比較対象をシナリオとして定義できるものであれば拡張できます。

## 2. 現在できること

- schema-first な JSON Schema / Pydantic models
- provider abstraction と local / OpenAI の切替
- local CSV / JSON / Markdown / text ingestion
- FAISS 優先の local RAG index / retrieval / grounding
- weighted config ベースの synthetic population generation
- survey / interview runner
- aggregation / scoring / markdown reporting
- demand estimation / inventory suggestion
- evaluation / calibration MVP
- Typer CLI と FastAPI 最小 API
- 東京圏スーパー新商品上市の sample flow

## 3. まだ未実装のこと

- 実データを使った強い calibration
- Claude / Gemini の本格 provider 実装
- 実ローカル LLM との接続実装
- 高度な geospatial reasoning
- 非同期 job orchestration
- 本格 UI
- 継続運用向け benchmark / backtest 蓄積

## 4. どう実現しているか

現在の MVP は、次のレイヤーで動いています。

1. `ingestion`
   local の CSV / JSON / Markdown / text と datasource metadata を読み込み、provenance-aware な正規化データへ変換します。

2. `RAG`
   正規化済みデータを chunk 化し、embedding を作り、FAISS 優先の local index に保存します。region / category / datasource metadata による絞り込みも行います。

3. `synthetic population`
   weighted config に基づいて、region、household、age band、income band、channel preference、price sensitivity などを持つ synthetic agents を複数生成します。

4. `survey / interview runner`
   scenario、agent profile、grounding context、prompt spec を結びつけて、structured JSON response を返します。

5. `aggregation / scoring`
   per-agent response を集約し、top reasons、top objections、segment summary、uncertainty summary を作ります。

6. `demand estimation / inventory suggestion`
   aggregated output をもとに、conservative / base / optimistic の range と inventory suggestion を返します。

7. `evaluation / calibration`
   expected distribution や benchmark と比較し、representativeness、stability、evidence coverage、bias risk を確認します。

## 5. 設定はどこでするか

設定に関係する場所は次の 4 つです。

### 5.1 `.env`

実行時の設定と secret を入れる場所です。

- provider の切替
- OpenAI API key
- chat / embedding model の指定
- timeout や retry

```bash
cp .env.example .env
```

主要項目:

- `RIA_MODEL_PROVIDER`
- `RIA_EMBEDDING_PROVIDER`
- `RIA_CHAT_MODEL`
- `RIA_EMBEDDING_MODEL`
- `OPENAI_API_KEY`
- `RIA_MODEL_CONFIG_PATH`

### 5.2 `configs/models/`

モデル実行の既定値を置く場所です。

- `default.toml`
- `openai.toml`
- `local.toml`
- `claude.toml`
- `gemini.toml`

### 5.3 `configs/providers/`

provider ごとの差分設定を置く場所です。

- base URL
- default model
- timeout
- retry

### 5.4 `configs/populations/`

synthetic population の分布設定を置く場所です。

- region weights
- age band weights
- household weights
- income band weights
- channel preference weights
- price sensitivity weights
- category conditioning

## OpenAI の設定方法

OpenAI を使う場合は `.env` に最低限次を設定します。

```env
RIA_MODEL_PROVIDER=openai
RIA_EMBEDDING_PROVIDER=openai
RIA_CHAT_MODEL=gpt-4.1-mini
RIA_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-key
```

必要に応じて以下も変更できます。

- `RIA_OPENAI_BASE_URL`
- `RIA_OPENAI_ORGANIZATION`
- `RIA_OPENAI_PROJECT`

## local の設定方法

現時点の `local` は **実ローカル大規模モデル接続ではなく、placeholder provider** です。
つまり、Ollama や vLLM のような実ローカル LLM にまだ直接つながるわけではありません。

現在の `local` は、以下の用途に向いています。

- 配線確認
- schema 確認
- pipeline の smoke test
- artifact の出力確認

設定例:

```env
RIA_MODEL_PROVIDER=local
RIA_EMBEDDING_PROVIDER=local
RIA_CHAT_MODEL=local-placeholder-chat
RIA_EMBEDDING_MODEL=local-placeholder-embedding
```

実ローカル LLM をつなぐ場合は、今後 `requirement_insight_agent/core/providers/` に provider 実装を追加する前提です。

## 6. 最短の使い方

### 6.1 まずインストールする

目的:
実行に必要な Python 環境と依存関係をそろえるためです。

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

### 6.2 sample data を取り込む

目的:
RAG や scenario 実行に使う元データを正規化して `data/processed/` に置くためです。

```bash
ria ingest
```

### 6.3 RAG index を作る

目的:
取り込んだデータを retrieval 可能にするためです。

```bash
ria build-index --input data/processed/normalized_records.json --output-dir .local/index/sample
```

### 6.4 synthetic population を作る

目的:
simulation の対象になる synthetic agents を複数生成するためです。

```bash
ria build-population \
  --config configs/populations/tokyo_mvp_population.json \
  --sample-size 24 \
  --category frozen_food \
  --output agents/sample_profiles/tokyo_mvp_population.sample.json
```

### 6.5 scenario を走らせる

目的:
agent に対して survey / interview を実行し、構造化応答を集めるためです。

```bash
ria run-scenario \
  --scenario examples/tokyo-supermarket-launch/scenario.json \
  --prompt prompts/survey/supermarket-launch-survey-v1.json \
  --population agents/sample_profiles/tokyo_mvp_population.sample.json \
  --index-dir .local/index/sample \
  --agent-limit 5 \
  --output .local/output/scenario_run.json \
  --jsonl-output .local/output/scenario_run.jsonl
```

### 6.6 集約する

目的:
individual response を、全体およびセグメント別の示唆に変換するためです。

```bash
ria aggregate \
  --run-result .local/output/scenario_run.json \
  --population agents/sample_profiles/tokyo_mvp_population.sample.json \
  --output .local/output/aggregated_output.json \
  --report .local/output/aggregation_report.md
```

### 6.7 需要レンジを出す

目的:
単一予測値ではなく、scenario-based な demand range と inventory suggestion を作るためです。

```bash
ria estimate-demand \
  --aggregation .local/output/aggregated_output.json \
  --base-units 900 \
  --output .local/output/demand_estimation.json \
  --report .local/output/demand_estimation_report.md
```

### 6.8 評価する

目的:
population や aggregated output を benchmark と比較し、未校正点や不安定さを確認するためです。

```bash
ria evaluate \
  --population agents/sample_profiles/tokyo_mvp_population.sample.json \
  --aggregation .local/output/aggregated_output.json \
  --benchmark evaluation/benchmarks/tokyo_mvp_expected_distribution.json \
  --output .local/output/evaluation_record.json \
  --report .local/output/evaluation_report.md
```

### 6.9 まとめて試す

もっと早く全体像を確認したい場合は、以下の 1 コマンドで sample workflow をまとめて実行できます。

```bash
ria run-example \
  --config examples/tokyo-supermarket-launch/example_config.json \
  --prompt-kind survey \
  --agent-limit 5 \
  --base-units 900 \
  --output-dir .local/examples/tokyo-supermarket-launch
```

## 7. 実行すると何が出るか

このプロジェクトの主な出力は **CLI が生成する JSON / JSONL / Markdown** です。
API を使う場合は、それらに相当する内容を JSON response として受け取ります。

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

## 8. CLI と API

### CLI

現在の主入口は CLI です。

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

### API

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

## 9. 倫理・安全・制約

- synthetic agents は実在人物ではない
- 実在個人の再構成・模倣・プロファイリングを目的としない
- 違法・不透明な scraping を前提にしない
- 結果は deterministic truth ではなく structured simulation result として扱う
- 高リスクな投資判断をこの出力単独で行わない

詳細は以下を参照してください。

- [docs/safety.md](docs/safety.md)
- [docs/data-policy.md](docs/data-policy.md)

### limitation

- local provider は placeholder 実装
- Claude / Gemini は abstraction のみで本実装は未完了
- calibration は benchmark scaffold 段階
- RAG は local index MVP に留まる
- aggregation / demand estimation は deterministic heuristic ベース
- report の品質は real-world validation に依存する

## 10. 関連ドキュメント

- [docs/getting-started.md](docs/getting-started.md)
- [docs/runbook.md](docs/runbook.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/schema-spec.md](docs/schema-spec.md)
- [docs/roadmap.md](docs/roadmap.md)

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

## License

Apache License 2.0