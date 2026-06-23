# Beginner Guide

この文書は、Requirement Insight Agent を初めて触る人向けの入門ガイドです。

README よりもさらに実務寄りに、次の 4 点だけを最初に分かるように整理しています。

- どこで設定するか
- どこに参考データを置くか
- どこに質問やシナリオを書くか
- 実行結果をどこで見るか

## まず最初に理解するとよいこと

このプロジェクトは、公開データや許諾済みデータを材料に synthetic consumer agents を作り、商品や施策に対する反応を比較するための CLI 中心のツールです。

重要なのは、単に「売れるかどうか」を断定するのではなく、次のような論点を事前に見比べることです。

- どの層が反応しやすいか
- どの価格帯で反応が鈍るか
- どの訴求が刺さりやすいか
- どの地域や販路で受け止められ方が変わるか

出力は予言ではなく、仮説整理と意思決定支援のための simulation result です。

## 先に答えだけ知りたい人へ

### 設定はどこか

- 実行時設定と API key は `.env`
- モデルの既定値は `configs/models/`
- provider ごとの設定は `configs/providers/`
- synthetic population の分布設定は `configs/populations/`

### 参考データはどこに置くか

- まずは `data/sample/` の sample data をそのまま使えます
- 自分のデータを使う場合は、CSV / JSON / Markdown / text を同様の場所に置いて ingest します
- ingest 後の正規化データは `data/processed/` に出ます

### 質問はどこに書くか

- シナリオ本体は `examples/tokyo-supermarket-launch/scenario.json`
- survey の質問は `prompts/survey/`
- interview の質問は `prompts/interview/`
- 補足の企画説明は `examples/tokyo-supermarket-launch/product_brief.md`
- 調べたい論点の整理は `examples/tokyo-supermarket-launch/research_questions.md`

### 結果はどこで見るか

- 通常の出力先は `.local/output/`
- サンプル一括実行の出力先は `.local/examples/tokyo-supermarket-launch/`
- 人がまず読むなら `aggregation_report.md`、`demand_estimation_report.md`、`evaluation_report.md` が見やすいです

## 最短で試す流れ

最初の 1 回は、細かく作り込まずに sample flow を通すのが分かりやすいです。

### 1. Python 環境を用意する

依存関係をインストールして、CLI を使えるようにします。

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

### 2. `.env` を作る

`.env.example` をコピーして `.env` を作ります。

```bash
cp .env.example .env
```

最初は local mode で十分です。

```env
RIA_MODEL_PROVIDER=local
RIA_EMBEDDING_PROVIDER=local
RIA_CHAT_MODEL=local-placeholder-chat
RIA_EMBEDDING_MODEL=local-placeholder-embedding
```

OpenAI を使う場合は、最低限次を設定します。

```env
RIA_MODEL_PROVIDER=openai
RIA_EMBEDDING_PROVIDER=openai
RIA_CHAT_MODEL=gpt-4.1-mini
RIA_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-key
```

## どこをどう設定するか

### `.env`

ここには、実行時に毎回効く設定を書きます。

- どの provider を使うか
- どの chat model / embedding model を使うか
- API key を何にするか
- timeout や retry をどうするか

最初に確認すれば十分な代表項目は次の通りです。

- `RIA_MODEL_PROVIDER`
- `RIA_EMBEDDING_PROVIDER`
- `RIA_CHAT_MODEL`
- `RIA_EMBEDDING_MODEL`
- `OPENAI_API_KEY`

### `configs/models/`

環境変数だけでなく、モデル構成の既定値そのものを変えたいときに使います。

たとえば、`default.toml`、`openai.toml`、`local.toml` があります。

### `configs/providers/`

provider ごとの接続先や timeout などを調整したいときに使います。

### `configs/populations/`

どんな synthetic consumer agents を作るかの分布設定です。

たとえば次のような重みを調整できます。

- 地域
- 年代
- 世帯構成
- 所得帯
- 購買チャネル嗜好
- 価格感度

## 参考データの置き場所

最初は `data/sample/` をそのまま使えば十分です。

このディレクトリには、ingest の元になる sample data が入っています。自分の案件に切り替えるときは、同じ考え方でローカルにデータを置きます。

使える形式は次の通りです。

- CSV
- JSON
- Markdown
- text

流れは次の通りです。

1. 元データを置く
2. `ria ingest` を実行する
3. 正規化結果が `data/processed/normalized_records.json` に出る
4. その正規化結果を使って index を作る

## 質問やシナリオはどこに書くか

このプロジェクトでは、質問は 1 か所ではなく役割ごとに分かれています。

### `examples/tokyo-supermarket-launch/scenario.json`

ここには、何を評価したいのかというシナリオ本体を書きます。

たとえば、次のような情報です。

- 対象商品
- 価格帯
- 想定チャネル
- 対象地域
- 比較したい施策や前提条件

### `prompts/survey/`

survey 形式で agent にどう尋ねるかを書く場所です。

### `prompts/interview/`

interview 形式で深掘りしたい場合の質問テンプレートです。

### `product_brief.md` と `research_questions.md`

この 2 つは補助資料です。

- `product_brief.md`: 商品や企画の背景説明
- `research_questions.md`: 今回の分析で何を明らかにしたいか

最初のカスタマイズ対象としては、次の 2 つを触るのが分かりやすいです。

1. `examples/tokyo-supermarket-launch/scenario.json`
2. `prompts/survey/supermarket-launch-survey-v1.json`

## 結果はどこで見るか

通常の CLI 実行では、主に `.local/output/` に成果物が出ます。

代表的なファイルは次の通りです。

- `scenario_run.json`: 各 agent の構造化応答
- `scenario_run.jsonl`: 1 行 1 レコードのログ形式
- `aggregated_output.json`: 集約済みの全体結果
- `aggregation_report.md`: 人が最初に読む要約レポート
- `demand_estimation.json`: 需要レンジと inventory suggestion
- `demand_estimation_report.md`: 需要レンジの説明用レポート
- `evaluation_record.json`: benchmark 比較を含む評価記録
- `evaluation_report.md`: 評価結果を読むためのレポート

一括サンプル実行の `ria run-example` を使う場合は、`.local/examples/tokyo-supermarket-launch/` にまとめて出ます。

## まず何から読めばよいか

最初に見る順番は次の通りです。

1. `aggregation_report.md`
2. `demand_estimation_report.md`
3. `evaluation_report.md`

理由は、JSON より Markdown のほうが全体像をつかみやすいからです。

JSON は、後から機械処理したいときや、詳細を検査したいときに見れば十分です。

## 実際のコマンド例

### とりあえず一式試す

```bash
ria run-example \
  --config examples/tokyo-supermarket-launch/example_config.json \
  --prompt-kind survey \
  --agent-limit 5 \
  --base-units 900 \
  --output-dir .local/examples/tokyo-supermarket-launch
```

### 1 ステップずつ確認しながら進める

```bash
ria ingest
ria build-index --input data/processed/normalized_records.json --output-dir .local/index/sample
ria build-population --config configs/populations/tokyo_mvp_population.json --sample-size 24 --category frozen_food --output agents/sample_profiles/tokyo_mvp_population.sample.json
ria run-scenario --scenario examples/tokyo-supermarket-launch/scenario.json --prompt prompts/survey/supermarket-launch-survey-v1.json --population agents/sample_profiles/tokyo_mvp_population.sample.json --index-dir .local/index/sample --agent-limit 5 --output .local/output/scenario_run.json --jsonl-output .local/output/scenario_run.jsonl
ria aggregate --run-result .local/output/scenario_run.json --population agents/sample_profiles/tokyo_mvp_population.sample.json --output .local/output/aggregated_output.json --report .local/output/aggregation_report.md
ria estimate-demand --aggregation .local/output/aggregated_output.json --base-units 900 --output .local/output/demand_estimation.json --report .local/output/demand_estimation_report.md
ria evaluate --population agents/sample_profiles/tokyo_mvp_population.sample.json --aggregation .local/output/aggregated_output.json --benchmark evaluation/benchmarks/tokyo_mvp_expected_distribution.json --output .local/output/evaluation_record.json --report .local/output/evaluation_report.md
```

## `run-example` と段階実行の使い分け

どちらを使うかは、目的で決めれば十分です。

### `ria run-example` だけでよい場合

次のどれかに当てはまるなら、まずは `ria run-example` だけで問題ありません。

- このプロジェクトが動くかどうかを確認したい
- どんな成果物が出るかだけ先に見たい
- sample data と sample scenario で全体像をつかみたい
- ingest、index、population、scenario 実行の細かい差分はまだ気にしない

この場合は、必要な設定をしてから 1 コマンド流せば十分です。

### `ingest` から順番に実行したほうがよい場合

次のどれかに当てはまるなら、段階実行のほうが向いています。

- 自分の参考データに差し替えたい
- scenario や prompt を自分の案件向けに調整したい
- どの段階で結果が変わったかを確認したい
- RAG の元データや population の作られ方を個別に検査したい
- 出力物を途中段階ごとに保存しながら比較したい

この場合は、`ria ingest` から順に実行していくほうが安全です。

### 迷ったときの結論

迷ったら、最初の 1 回は `ria run-example`、自分の案件に置き換える段階で `ingest` からの段階実行に切り替える、という理解で十分です。

## よくある迷いどころ

### local と OpenAI はどちらを使えばよいか

最初の確認だけなら local で十分です。配線、schema、出力物の形を確認できます。

実際に LLM を使った応答品質も見たいなら OpenAI に切り替えます。

### 自分の案件では最初に何を変えるべきか

最初に変える優先度は次の通りです。

1. `scenario.json`
2. prompt 定義
3. 参考データ
4. population config

### どの結果を信じればよいか

まず見るべきなのは、単一の数値よりも次の情報です。

- どういう層が反応しているか
- どの objection が強いか
- どの grounding が根拠として使われたか
- evaluation でどの未校正点が残っているか

## 次に読むとよい文書

- `docs/getting-started.md`: さらに短い最短手順
- `docs/runbook.md`: 運用時の実務手順
- `docs/architecture.md`: 実装構造の理解
- `docs/data-policy.md`: データの扱い方
- `docs/evaluation.md`: 評価の見方
