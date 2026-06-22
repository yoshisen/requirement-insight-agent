# Architecture

## 目的

この文書は、**Requirement Insight Agent** の実装アーキテクチャを定義するための設計文書である。  
README.md を上位仕様（source of truth）とし、本書はその内容を**実装可能な構造に落とし込む技術仕様**として位置付ける。

本プロジェクトは、公開データ・RAG・synthetic consumer agents・マルチモデル実行を組み合わせて、  
**市場要求の探索、需要仮説の形成、シナリオ評価、意思決定支援**を行うための OSS である。

ただし本プロジェクトは以下を厳守する。

- 本システムは研究・仮説生成・意思決定支援のためのものであり、現実の市場調査の代替ではない
- synthetic agents は実在個人ではなく、実在個人の再構成・模倣・プロファイリングを目的としない
- 出力は deterministic truth ではなく、**scenario-based insights with uncertainty** として扱う
- データ利用は適法・監査可能・ライセンス準拠でなければならない

---

## 1. システム全体像

Requirement Insight Agent は、以下の大きな流れで構成される。

1. 公開データ・地域データ・商品データ・ユーザー提供資料を取り込む
2. データを正規化し、出所・ライセンス・地域・時点などの metadata を付与する
3. 文書知識を knowledge base / vector index として保持する
4. 対象市場に整合する synthetic population を生成する
5. scenario と問い（survey / interview）をもとに、各 agent に対して RAG-grounded な応答を生成する
6. 応答を集約し、セグメント別示唆・異論・価格感度・チャネル傾向などを整理する
7. シナリオに応じて需要レンジ・在庫示唆などを区間付きで推定する
8. benchmark / calibration / evaluation を通じて出力の妥当性を検証する
9. CLI / API / 将来の UI を通じて実行・再現・保存する

---

## 2. 設計原則

### 2.1 Population-aligned
agent は“キャラクター”ではなく、**母集団分布に整合した合成的表現体**である。

### 2.2 Grounded
応答は可能な限り、統計・カテゴリ知識・地域知識・商品知識に grounding されるべきである。

### 2.3 Explainable
各出力には、前提・根拠・不確実性・典拠の trace を付与できる構造を持たせる。

### 2.4 Modular
data ingestion、RAG、agent generation、model provider、aggregation、evaluation は交換可能なモジュールとして設計する。

### 2.5 Reproducible
プロンプト、モデル、設定、シード、データ版を記録し、再実行可能性を確保する。

### 2.6 Safety-first
個人再構成、差別的推定、違法スクレイピング、不透明な data use を避ける。

### 2.7 Human-in-the-loop
本システムは最終意思決定システムではなく、人間による検証・判断を前提とする。

---

## 3. レイヤー構成

システムは以下のレイヤーで構成する。

```text
+------------------------------------------------------+
|                  User / CLI / API                    |
+-----------------------------+------------------------+
                              |
                              v
+------------------------------------------------------+
|              Scenario Execution Layer                |
|   survey / interview / simulation / orchestration    |
+-----------------------------+------------------------+
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v
+------------------------------+   +-------------------------------+
|   Synthetic Population Layer |   |       Knowledge / RAG Layer  |
|   persona generation         |   | retrieval / grounding        |
|   traits / uncertainty       |   | citations / context builder  |
+------------------------------+   +-------------------------------+
          |                                       |
          +-------------------+-------------------+
                              |
                              v
+------------------------------------------------------+
|         Aggregation / Scoring / Estimation           |
|   summaries / ranges / confidence / objections       |
+-----------------------------+------------------------+
                              |
                              v
+------------------------------------------------------+
|        Evaluation / Calibration / Monitoring         |
+-----------------------------+------------------------+
                              |
                              v
+------------------------------------------------------+
|             Storage / Metadata / Provenance          |
+-----------------------------+------------------------+
                              ^
                              |
+------------------------------------------------------+
|           Ingestion / Normalization / Indexing       |
+------------------------------------------------------+
```

## 4. 各レイヤーの責務

### 4.1 Ingestion Layer

#### 責務

- 外部データを収集・読込する
- 形式差異を吸収する
- provenance を記録する
- ライセンス / allowed_use を保持する

#### 主な入力

- CSV / JSON / Markdown / text
- 公開統計の要約データ
- 地域データ
- 商品情報
- ユーザー提供資料

#### 主な出力

- 正規化可能な raw records
- source metadata
- file-level provenance

#### 想定ディレクトリ

- ingestion/
- data/raw/
- data/sample/

#### 注意点

- scraping はシステム前提にしない
- 個人再構成につながる data collection を禁止
- “公開されている”ことと“自由利用可能”は同義ではない

### 4.2 Normalization Layer

#### 責務

- データを内部共通形式へ変換する
- 地域 / カテゴリ / 時点 / 典拠ラベルを付与する
- quality score や known biases を扱う

#### 主な入力

- ingestion layer の raw data
- datasource metadata

#### 主な出力

- normalized documents
- normalized structured records
- provenance-aware objects

#### 想定ディレクトリ

- ingestion/
- data/processed/

### 4.3 Knowledge Base / Corpus Layer

#### 責務

- テキスト知識を保存する
- 構造化 metadata と一体で保持する
- RAG 可能な corpus を作る

#### 主な入力

- 正規化済み documents
- 商品説明
- 地域メモ
- 調査補助資料

#### 主な出力

- chunked text units
- indexed document set
- metadata-rich knowledge objects

#### 想定ディレクトリ

- rag/indexing/
- data/processed/

### 4.4 RAG / Retrieval Layer

#### 責務

- region / category / scenario に応じて relevant context を取得する
- retrieved evidence を citation trace として保持する
- 根拠不足時は uncertainty を上げる

#### 主な入力

- scenario
- agent attributes
- query template
- indexed corpus

#### 主な出力

- retrieval result set
- grounding context bundle
- citation references

#### 想定ディレクトリ

- rag/retrieval/
- rag/grounding/

#### 重要

- RAG は“説得のための補強”ではなく、“根拠不足を検出するための制約機構”としても使う
- grounding 不十分なときに、無理に断定させない

### 4.5 Synthetic Population / Persona Generation Layer

#### 責務

- population-aligned な synthetic agents を生成する
- distribution-based な traits を割り当てる
- region / household / income / shopping style などを保持する
- uncertainty を agent 単位で管理する

#### 主な入力

- population config
- regional distribution assumptions
- category priors
- optional benchmark data

#### 主な出力

- synthetic agents
- synthetic population set
- generation metadata

#### 想定ディレクトリ

- agents/builders/
- agents/
- configs/

#### 重要

- 実在人物を模倣しない
- SNS等から具体的個人を復元しない
- fiction は抽象アーキタイプ着想程度に留める

### 4.6 Agent Orchestration Layer

#### 責務

- 各 synthetic agent に対する質問実行を制御する
- single-turn / multi-turn interview を扱う
- model provider を透過的に切替える
- retry / guardrail / structured output を扱う

#### 主な入力

- synthetic agent
- scenario
- survey/interview prompt spec
- grounding context

#### 主な出力

- per-agent responses
- response metadata
- model execution trace

#### 想定ディレクトリ

- agents/orchestration/
- prompts/
- simulations/

### 4.7 Survey / Interview Simulation Layer

#### 責務

- アンケート質問・インタビュー質問を定義して実行する
- JSON 構造化出力を収集する
- 購買意向・価格反応・ objection・ preferred channel などを記録する

#### 主な入力

- question spec
- agent
- context
- scenario

#### 主な出力

- survey response records
- interview transcripts（必要に応じて）
- structured reasoning output

### 4.8 Aggregation / Scoring Layer

#### 責務

- agent 応答を全体・セグメント別に集約する
- top reasons / objections / sensitivities を抽出する
- disagreement / variance を追跡する

#### 主な入力

- per-agent response records
- agent metadata
- scenario metadata

#### 主な出力

- aggregate summaries
- segment summaries
- scored signals
- uncertainty summary

#### 想定ディレクトリ

- simulations/aggregation.py
- simulations/scoring.py
- simulations/reporting.py

### 4.9 Scenario Simulation Layer

#### 責務

- 条件違い（価格、チャネル、訴求、地域など）を比較する
- conservative / base / optimistic ケースを評価する
- 反実仮想シナリオを構造的に扱う

#### 主な入力

- scenario definitions
- aggregated responses
- optional assumptions

#### 主な出力

- scenario comparison result
- condition sensitivity
- demand estimation input

### 4.10 Demand Estimation Layer

#### 責務

- 集約結果を business-friendly なレンジ出力に変換する
- inventory suggestion を range として返す
- assumptions と uncertainty を明示する

#### 主な入力

- aggregated insights
- scenario assumptions
- optional baseline business metrics

#### 主な出力

- conservative/base/optimistic ranges
- inventory suggestion ranges
- assumptions
- risk factors
- confidence level

#### 重要

- 予測 engine ではなく scenario estimator として扱う
- 単一の deterministic 値を返さない

### 4.11 Evaluation / Calibration Layer

#### 責務

- synthetic population が distribution に整合しているか確認する
- output stability を確認する
- benchmark と比較する
- calibration のための補正情報を保持する

#### 主な入力

- generated population
- expected distributions
- scenario results
- optional real-world survey data

#### 主な出力

- representativeness metrics
- calibration report
- stability report
- known limitations report

#### 重要

- このレイヤーがなければ、本システムは“会話生成器”に留まる
- calibration は MVP では簡易でも必須

### 4.12 API / CLI / UI Layer

#### 責務

- システム利用者への入口を提供する
- CLI で end-to-end 実行を可能にする
- API で将来 UI や外部アプリ接続を可能にする

#### MVP優先順位

- CLI
- Minimal FastAPI
- UI（将来）

## 5. データフロー

```text
external data
 /inventory ranges  -> ingestion
                        -> evaluation/calibration
    -> normalization
      -> processed corpus / structured records
        -> indexing
          -> retrieval
            -> grounding context
              -> agent execution
                -> structured responses
                  -> aggregation
                    -> scenario estimation
```

## 6. 実行フロー（MVP）

MVP の end-to-end フローは以下を想定する。

1. `ingest`

   sample data またはユーザー提供データを取り込む

2. `build-index`

   knowledge corpus を chunk 化・埋め込み・index 化する

3. `build-population`

   東京圏向けの synthetic population を生成する

4. `run-scenario`

   商品/価格/カテゴリ/地域を指定して質問実行する

5. `aggregate`

   結果をセグメント別に集約する

6. `estimate-demand`

   conservative / base / optimistic のレンジを推定する

7. `evaluate`

   distribution / output stability / uncertainty を確認する

## 7. モジュール間 I/O

### 7.1 Ingestion -> Normalization

#### 入力

- raw files
- datasource metadata

#### 出力

- normalized records
- document objects
- source provenance

### 7.2 Normalization -> RAG

#### 入力

- normalized text corpus
- metadata

#### 出力

- chunk units
- vector index entries
- filterable document store

### 7.3 Population Builder -> Orchestration

#### 入力

- population config
- distribution assumptions

#### 出力

- synthetic agent objects
- population metadata

### 7.4 RAG -> Agent Execution

#### 入力

- scenario query
- agent profile
- retrieval request

#### 出力

- grounding context bundle
- citation refs
- uncertainty hints

### 7.5 Agent Execution -> Aggregation

#### 入力

- structured per-agent responses

#### 出力

- segment summaries
- scored intents
- reasons / objections clusters

### 7.6 Aggregation -> Demand Estimation

#### 入力

- aggregate result
- assumptions
- scenario conditions

#### 出力

- demand ranges
- inventory suggestion ranges
- risk flags

### 7.7 All Layers -> Evaluation

#### 入力

- population
- outputs
- benchmarks
- run configs

#### 出力

- evaluation reports
- calibration recommendations

## 8. 不確実性の保持ポイント

本システムでは不確実性を hidden にせず、構造的に保持する。

不確実性を保持すべき箇所

### Data layer

- データ鮮度
- 地域粒度
- coverage の欠損
- source bias

### Population layer

- profile ambiguity
- latent preference uncertainty
- category familiarity uncertainty

### RAG layer

- retrieval confidence
- evidence sparsity
- citation consistency

### Response layer

- self-reported confidence
- contradictory signals
- insufficient grounding

### Aggregation layer

- high disagreement
- segment instability
- low sample robustness

### Demand estimation layer

- assumptions sensitivity
- scenario fragility
- low-confidence warning

## 9. Calibration をどこで行うか

Calibration は単一箇所ではなく、複数フェーズにまたがる。

### 9.1 Population calibration

- 年齢帯
- 世帯構成
- 所得帯
- 地域分布
- channel preference

### 9.2 Response calibration

- known category trends
- known price sensitivity patterns
- historical survey alignment

### 9.3 Output calibration

- benchmark scenario comparison
- historical launch outcome comparison
- run-to-run stability check

### 9.4 レイヤー責務

- population calibration: agents/ + evaluation/
- response/output calibration: evaluation/ + simulations/

## 10. 実在個人再構成を避けるための設計制約

本プロジェクトでは以下をアーキテクチャ制約として組み込む。

- individual reconstruction を目的としない
- 直接的 personal data ingestion を前提にしない
- 特定アカウント由来の人格模倣を禁止
- fictional character の直接コピーを禁止
- 属性は aggregate distribution から生成
- agent profile は “representative synthetic pattern” として扱う
- response generation 時に “あなたは実在人物ではない synthetic market agent である” という system constraint を入れる
- sensitive targeting を業務目的にしない

## 11. Multi-model Provider Abstraction の位置づけ

モデル依存性を抑えるため、provider abstraction を設ける。

### 目的

- OpenAI / Gemini / Claude / local model の差異吸収
- cost/performance routing
- fallback
- deterministic/stochastic mode の切替

### 置き場所（案）

- core/providers/
- core/config.py

### 抽象対象

- chat generation
- structured output generation
- embeddings
- token / cost metadata

### 重要

- orchestration 層は provider の詳細を知らない
- provider 変更で prompt や pipeline 全体を壊さない構造にする

## 12. RAG Grounding の制御点

RAG は agent 応答の中核的制御点の一つである。

### 制御する内容

- どの region の情報を優先するか
- どの category の知識を使うか
- どの時点データを使うか
- どの出所を優先するか
- citation をどこまで残すか
- 根拠不足時の fallback 文言

### ガードレール

- 根拠がない推測は低 confidence 扱い
- retrieved evidence を explanation trace に保存
- 典拠抜きの断定を避ける

## 13. 推奨ディレクトリと責務対応

- docs/                設計仕様、方針文書
- configs/             モデル・pipeline・scenario 設定
- schemas/             JSON Schema / data contracts
- data/raw/            生データ
- data/processed/      正規化済みデータ
- data/sample/         サンプルデータ
- ingestion/           データ取り込み・正規化
- rag/                 indexing / retrieval / grounding
- agents/              synthetic population / memory / orchestration
- prompts/             survey / interview / aggregation prompts
- simulations/         scenario execution / aggregation / estimation
- evaluation/          benchmark / calibration / metrics
- api/                 FastAPI などの外部インターフェース
- examples/            再現可能なサンプルケース
- tests/               単体・統合テスト

## 14. MVP と将来版の境界

### MVP で実装するもの

- 東京圏向けサンプルデータ ingest
- 基本的な RAG
- 20〜100程度の synthetic agents
- 1カテゴリ（例: スーパー新商品）
- CLI による scenario 実行
- 簡易 aggregation
- conservative/base/optimistic の demand range
- 簡易 evaluation / calibration

### 将来版で追加するもの

- 1000+ agents
- multi-region support
- asynchronous job management
- UI dashboard
- stronger calibration against real-world benchmarks
- richer geospatial reasoning
- continuous updating pipelines
- human evaluator workflow

## 15. 失敗しやすい設計上の落とし穴

- synthetic population を“キャラクター集”にしてしまう
- RAG を citation 装飾としてしか使わない
- calibration を後回しにして narrative system になる
- deterministic な需要推奨値を返してしまう
- provider 差異を吸収しないまま orchestration に埋め込む
- 倫理・ライセンス制約を data ingestion に反映しない
- agent ごとの explanation trace を捨ててしまう

## 16. 実装優先順位

推奨順:

1. docs/schema-spec.md
2. repository skeleton
3. JSON Schema / Pydantic models
4. config + provider abstraction
5. ingestion
6. RAG
7. synthetic population builder
8. survey/interview runner
9. aggregation
10. demand estimation
11. evaluation / calibration
12. CLI
13. example scenario
14. API

## 17. 最終メモ

このアーキテクチャは、“市場を完全再現するシステム” を目指すものではない。
目指すのは、仮説、異論、説明可能な不確実性を伴う market insight workflow を OSS として構築することである。
そのために、構造は以下を同時に満たす必要がある。

- 実装しやすいこと
- 安全であること
- 校正できること
- 誤用しにくいこと
- 研究・業務双方で拡張しやすいこと

