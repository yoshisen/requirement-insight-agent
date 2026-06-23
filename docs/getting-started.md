# Getting Started

この文書は、Requirement Insight Agent を初めて触る人向けの最短ガイドです。

## 1. インストール

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

## 2. `.env` を作る

```bash
cp .env.example .env
```

まずは local mode のままで十分です。

```env
RIA_MODEL_PROVIDER=local
RIA_EMBEDDING_PROVIDER=local
```

## 3. sample data を ingest する

```bash
ria ingest
```

出力:

- `data/processed/normalized_records.json`

## 4. RAG index を作る

```bash
ria build-index --input data/processed/normalized_records.json --output-dir .local/index/sample
```

## 5. synthetic population を作る

```bash
ria build-population --config configs/populations/tokyo_mvp_population.json --sample-size 24 --category frozen_food --output agents/sample_profiles/tokyo_mvp_population.sample.json
```

## 6. sample scenario を走らせる

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

## 7. 集約・需要推定・評価を出す

```bash
ria aggregate --run-result .local/output/scenario_run.json --population agents/sample_profiles/tokyo_mvp_population.sample.json --output .local/output/aggregated_output.json --report .local/output/aggregation_report.md
ria estimate-demand --aggregation .local/output/aggregated_output.json --base-units 900 --output .local/output/demand_estimation.json --report .local/output/demand_estimation_report.md
ria evaluate --population agents/sample_profiles/tokyo_mvp_population.sample.json --aggregation .local/output/aggregated_output.json --benchmark evaluation/benchmarks/tokyo_mvp_expected_distribution.json --output .local/output/evaluation_record.json --report .local/output/evaluation_report.md
```

## 8. もっと早く試す

```bash
ria run-example --config examples/tokyo-supermarket-launch/example_config.json --prompt-kind survey --output-dir .local/examples/tokyo-supermarket-launch
```

## よくあるエラー

- `ModuleNotFoundError`
  - virtual environment が有効か確認してください。

- `OPENAI_API_KEY is required`
  - OpenAI mode にしているのに API key が未設定です。local mode に戻すか key を入れてください。

- `Artifact not found`
  - 前段コマンドの output path を確認してください。

- `No indexed chunks matched the provided filters`
  - `ria retrieve-test` や `ria run-scenario` で region / category の条件が厳しすぎる可能性があります。