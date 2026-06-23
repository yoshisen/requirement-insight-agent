# Runbook

この文書は、開発者向けの運用手順書です。

## 1. 推奨実行順

1. `ria ingest`
2. `ria build-index`
3. `ria build-population`
4. `ria run-scenario`
5. `ria aggregate`
6. `ria estimate-demand`
7. `ria evaluate`

## 2. sample flow の一括実行

```bash
ria run-example --config examples/tokyo-supermarket-launch/example_config.json --prompt-kind survey --agent-limit 5 --base-units 900 --output-dir .local/examples/tokyo-supermarket-launch
```

## 3. API 起動

```bash
python -m uvicorn api.app:app --reload
```

主要 endpoint:

- `GET /health`
- `POST /population/build`
- `POST /scenario/run`
- `POST /examples/tokyo-supermarket-launch/run`
- `GET /results/{artifact_name}`

## 4. local / OpenAI 切替

### local

```env
RIA_MODEL_PROVIDER=local
RIA_EMBEDDING_PROVIDER=local
```

### OpenAI

```env
RIA_MODEL_PROVIDER=openai
RIA_EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=...
```

## 5. 主要成果物の場所

- `data/processed/normalized_records.json`
- `.local/index/sample/`
- `agents/sample_profiles/tokyo_mvp_population.sample.json`
- `.local/output/scenario_run.json`
- `.local/output/aggregated_output.json`
- `.local/output/demand_estimation.json`
- `.local/output/evaluation_record.json`

## 6. 発生しやすいエラーと対処

### 6.1 文字化け

PowerShell で UTF-8 の日本語が崩れることがあります。ファイル本体は UTF-8 で保存されているため、エディタ側で確認してください。

### 6.2 FAISS が使えない

`faiss-cpu` が使えない環境でも numpy fallback で retrieval 自体は動きます。

### 6.3 sample output が見つからない

`.local/` 以下は都度生成物です。先に前段の CLI を実行してください。

### 6.4 provider authentication error

OpenAI を選んでいるのに `OPENAI_API_KEY` がない場合に起きます。local mode に戻すか key を設定してください。

## 7. テスト

focused regression:

```bash
python -m pytest tests/test_ingestion.py tests/test_rag_chunking.py tests/test_rag_retrieval.py tests/test_population_builder.py tests/test_population_cli.py tests/test_runner_models.py tests/test_scenario_runner.py tests/test_run_scenario_cli.py tests/test_aggregation.py tests/test_aggregate_cli.py tests/test_demand_estimation.py tests/test_estimate_demand_cli.py tests/test_evaluation.py tests/test_evaluate_cli.py tests/test_api.py tests/test_typer_main.py
```

## 8. 今後の運用上の注意

- calibration 前の出力を business truth として扱わない
- benchmark file と expected distribution を定期的に見直す
- prompt spec を更新したら runner と aggregation の期待出力を再確認する
- report 文面の自然さより、structured trace の保存を優先する