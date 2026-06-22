# Schema Specification

## 目的

この文書は、Requirement Insight Agent における主要スキーマの仕様を定義する。  
README.md および `docs/architecture.md` に整合し、後続で以下へ実装されることを想定する。

- JSON Schema
- Pydantic v2 models
- internal validation contracts
- API request / response models

本仕様は、**MVPで必要な最小構成**を優先しつつ、将来拡張を妨げないことを目的とする。

---

## 設計方針

### 1. Schema first
スキーマは単なる入出力定義ではなく、設計制約・安全制約・ provenance 管理の基盤とする。

### 2. MVP first
最初から全項目を必須にせず、MVPで成立する最小構成を設計する。

### 3. Explainability aware
結果スキーマには、reason / objection / citation / uncertainty / explanation trace を保持できるようにする。

### 4. Safety aware
実在個人の再構成につながる構造を避ける。

### 5. Extensible
地域拡張・カテゴリ拡張・ multi-model 対応・ calibration 強化に備えて optional fields を設計する。

---

# 1. Synthetic Consumer Agent Schema

## 1.1 目的

synthetic consumer agent を構造化表現する。  
この schema は実在人物のプロフィールではなく、**母集団整合型の合成消費者表現体**を扱う。

---

## 1.2 主な用途

- population generation の保存
- scenario 実行時の agent input
- aggregation / segmentation のキー
- calibration / evaluation の対象

---

## 1.3 最小スキーマ（MVP）

### 必須フィールド

- `agent_id`
- `region`
- `age_band`
- `household_composition`
- `income_band`
- `channel_preference`
- `price_sensitivity`
- `category_preferences`
- `uncertainty_profile`
- `response_style`
- `metadata`

### 任意フィールド

- `life_stage`
- `occupation_style`
- `mobility_pattern`
- `basket_size_tendency`
- `impulse_purchase_tendency`
- `planning_tendency`
- `brand_loyalty_tendency`
- `novelty_seeking`
- `health_orientation`
- `eco_orientation`
- `convenience_orientation`
- `risk_aversion`
- `digital_literacy`
- `constraints`
- `rationale_memory`
- `grounding_context_refs`
- `worldview_tags`

---

## 1.4 フィールド仕様

### `agent_id`
- 型: `string`
- 必須: はい
- 説明: agent の一意識別子
- 例: `"tokyo-agent-0001"`

### `region`
- 型: `string`
- 必須: はい
- 説明: 地域・商圏・行政単位の表現
- 例: `"tokyo-metropolitan"`, `"tokyo-west-suburban"`

### `catchment_area`
- 型: `string | null`
- 必須: いいえ
- 説明: より具体的な生活圏・商圏ラベル

### `age_band`
- 型: `string`
- 必須: はい
- 例: `"20s"`, `"30s"`, `"40s"`, `"50s"`, `"60_plus"`

### `household_composition`
- 型: `string`
- 必須: はい
- 例:
  - `"single"`
  - `"couple"`
  - `"family_with_children"`
  - `"elderly_household"`

### `life_stage`
- 型: `string | null`
- 必須: いいえ
- 例:
  - `"student"`
  - `"early_career"`
  - `"child_raising"`
  - `"post_retirement"`

### `income_band`
- 型: `string`
- 必須: はい
- 例:
  - `"low"`
  - `"lower_middle"`
  - `"middle"`
  - `"upper_middle"`
  - `"high"`

### `occupation_style`
- 型: `string | null`
- 必須: いいえ
- 例:
  - `"office_worker"`
  - `"shift_worker"`
  - `"freelance"`
  - `"homemaker"`
  - `"retired"`

### `mobility_pattern`
- 型: `string | null`
- 必須: いいえ
- 例:
  - `"walk_or_bike"`
  - `"public_transport"`
  - `"car_dependent"`
  - `"hybrid"`

### `channel_preference`
- 型: `string`
- 必須: はい
- 例:
  - `"offline_first"`
  - `"online_first"`
  - `"hybrid"`

### `price_sensitivity`
- 型: `string`
- 必須: はい
- 例:
  - `"low"`
  - `"medium"`
  - `"high"`

### `shopping_mission_types`
- 型: `array[string]`
- 必須: いいえ
- 例:
  - `["daily_restock", "bulk_buying", "planned_purchase"]`

### `category_preferences`
- 型: `array[string]`
- 必須: はい
- 例:
  - `["frozen_food", "healthy_food", "household_goods"]`

### `category_aversions`
- 型: `array[string]`
- 必須: いいえ

### `brand_loyalty_tendency`
- 型: `string | null`
- 必須: いいえ
- 例:
  - `"low"`
  - `"medium"`
  - `"high"`

### `novelty_seeking`
- 型: `string | null`
- 必須: いいえ

### `basket_size_tendency`
- 型: `string | null`
- 必須: いいえ
- 例:
  - `"small"`
  - `"medium"`
  - `"large"`

### `impulse_purchase_tendency`
- 型: `string | null`
- 必須: いいえ

### `planning_tendency`
- 型: `string | null`
- 必須: いいえ

### `digital_literacy`
- 型: `string | null`
- 必須: いいえ

### `health_orientation`
- 型: `string | null`
- 必須: いいえ

### `eco_orientation`
- 型: `string | null`
- 必須: いいえ

### `convenience_orientation`
- 型: `string | null`
- 必須: いいえ

### `risk_aversion`
- 型: `string | null`
- 必須: いいえ

### `constraints`
- 型: `object | null`
- 必須: いいえ
- 例:
  - `budget_constraints`
  - `time_constraints`
  - `storage_constraints`
  - `access_constraints`

### `rationale_memory`
- 型: `array[object] | null`
- 必須: いいえ
- 説明: 過去の scenario 実行や reasoning cue を蓄えるための拡張領域

### `grounding_context_refs`
- 型: `array[string] | null`
- 必須: いいえ
- 説明: 参照されやすい背景知識の識別子

### `uncertainty_profile`
- 型: `object`
- 必須: はい
- 最低限の推奨キー:
  - `profile_confidence: string`
  - `preference_uncertainty: string`
  - `category_familiarity: string`

### `response_style`
- 型: `object`
- 必須: はい
- 最低限の推奨キー:
  - `verbosity`
  - `directness`
  - `confidence_expression`

### `metadata`
- 型: `object`
- 必須: はい
- 最低限の推奨キー:
  - `generated_at`
  - `generator_version`
  - `population_config_id`
  - `seed`

---

## 1.5 MVP 最小例

```json
{
  "agent_id": "tokyo-agent-0001",
  "region": "tokyo-metropolitan",
  "age_band": "30s",
  "household_composition": "single",
  "income_band": "middle",
  "channel_preference": "hybrid",
  "price_sensitivity": "medium",
  "category_preferences": ["frozen_food", "healthy_food"],
  "uncertainty_profile": {
    "profile_confidence": "medium",
    "preference_uncertainty": "medium",
    "category_familiarity": "high"
  },
  "response_style": {
    "verbosity": "medium",
    "directness": "medium",
    "confidence_expression": "cautious"
  },
  "metadata": {
    "generated_at": "2026-06-22T10:00:00Z",
    "generator_version": "0.1.0",
    "population_config_id": "tokyo-mvp-v1",
    "seed": 42
  }
}
```

## 1.6 バリデーション方針

- agent_id は一意
- age_band, income_band, channel_preference, price_sensitivity は enum 推奨
- category_preferences は空配列不可（MVPでは最低1件）
- uncertainty_profile と response_style は必須
- センシティブ属性推定へつながる direct field は追加しない


## 1.7 安全上の制約

- 実名・個人識別子を保持しない
- SNSアカウント由来のプロファイルを直接保存しない
- 実在人物の行動履歴のような表現を持ち込まない
- worldview は抽象タグに留め、センシティブな政治・宗教・民族などを直接最適化対象にしない


## 2. Data Source Metadata Schema

### 2.1 目的
外部データ・内部データ・ sample データの出所・利用条件・鮮度・品質を追跡する。

### 2.2 必須フィールド

- `datasource_id`
- `source_name`
- `source_type`
- `license_type`
- `allowed_use`
- `retrieved_at`
- `coverage_region`
- `quality_score`
- `provenance`


### 2.3 フィールド仕様

#### `datasource_id`

- 型: string
- 例: `"tokyo-household-sample-001"`

#### `source_name`

- 型: string

#### `source_type`

- 型: string
- 例:

- `"government_statistics"`
- `"geospatial"`
- `"product_catalog"`
- `"survey_results"`
- `"market_notes"`



#### `source_url`

- 型: string | null

#### `license_type`

- 型: string
- 例:

- `"public"`
- `"cc-by"`
- `"internal"`
- `"restricted"`
- `"unknown"`



#### `allowed_use`

- 型: array[string]
- 例:

- `["research", "internal_analysis"]`



#### `retrieved_at`

- 型: string (datetime)

#### `coverage_region`

- 型: array[string]

#### `coverage_time`

- 型: string | null

#### `language`

- 型: string | null

#### `format`

- 型: string | null
- 例: `"csv"`, `"json"`, `"md"`

#### `quality_score`

- 型: number
- 範囲: 0.0 - 1.0

#### `known_biases`

- 型: array[string] | null

#### `provenance`

- 型: object
- 推奨キー:

- `collected_by`
- `collected_method`
- `notes`

```json
{
  "datasource_id": "sample-market-note-001",
  "source_name": "Tokyo Frozen Food Market Notes",
  "source_type": "market_notes",
  "license_type": "internal",
  "allowed_use": ["research", "prototype"],
  "retrieved_at": "2026-06-22T10:00:00Z",
  "coverage_region": ["tokyo-metropolitan"],
  "quality_score": 0.7,
  "provenance": {
    "collected_by": "project-team",
    "collected_method": "manual_import",
    "notes": "sample data for MVP"
  }
}
```


### 2.5 バリデーション方針

- quality_score は 0〜1
- allowed_use は空配列不可推奨
- license_type 不明時は `"unknown"` として明示
- provenance を欠落させない


## 3. Scenario Schema

### 3.1 目的
ある市場仮説検証タスクを定義する。
例: 「東京圏で高たんぱく低糖質の冷凍惣菜をスーパーで上市すべきか」

### 3.2 必須フィールド

- `scenario_id`
- `title`
- `region`
- `category`
- `business_question`
- `target_agents`
- `product_or_service`
- `evaluation_dimensions`
- `assumptions`
- `metadata`


### 3.3 フィールド仕様

#### `scenario_id`

- 型: string

#### `title`

- 型: string

#### `region`

- 型: array[string]
- 例: `["tokyo-metropolitan"]`

#### `category`

- 型: array[string]
- 例: `["supermarket", "frozen_food"]`

#### `business_question`

- 型: string

#### `product_or_service`

- 型: object
- 最低限推奨キー:

- `name`
- `description`
- `price_options`
- `positioning`



#### `comparison_targets`

- 型: array[string] | null

#### `target_agents`

- 型: object
- 推奨キー:

- `population_id`
- `selection_filters`
- `sample_size`



#### `evaluation_dimensions`

- 型: array[string]
- 例:

- `["purchase_intent", "price_sensitivity", "channel_preference", "objections"]`



#### `assumptions`

- 型: array[string]

#### `constraints`

- 型: array[string] | null

#### `scenario_variants`

- 型: array[object] | null
- 例:

- price variant
- channel variant
- promotion variant



#### `metadata`

- 型: object
- 推奨キー:

- `created_at`
- `created_by`
- `version`




### 3.4 MVP 最小例

```json
{
  "scenario_id": "tokyo-supermarket-launch-001",
  "title": "東京圏スーパー新商品上市評価",
  "region": ["tokyo-metropolitan"],
  "category": ["supermarket", "frozen_food"],
  "business_question": "東京圏で新しい高たんぱく低糖質の冷凍惣菜を上市すべきか",
  "product_or_service": {
    "name": "Protein Frozen Dish",
    "description": "高たんぱく・低糖質・時短向け冷凍惣菜",
    "price_options": [398, 498, 598],
    "positioning": "healthy_convenient_meal"
  },
  "target_agents": {
    "population_id": "tokyo-mvp-v1",
    "selection_filters": {},
    "sample_size": 20
  },
  "evaluation_dimensions": [
    "purchase_intent",
    "price_sensitivity",
    "channel_preference",
    "objections"
  ],
  "assumptions": [
    "東京圏のスーパーで販売する",
    "初期販促は限定的"
  ],
  "metadata": {
    "created_at": "2026-06-22T10:00:00Z",
    "created_by": "project-team",
    "version": "0.1"
  }
}
```

### 3.5 バリデーション方針

- region と category は最低1つ以上
- evaluation_dimensions は空にしない
- price_options は数値配列推奨
- sample_size は正の整数


## 4. Survey / Interview Prompt Specification Schema

### 4.1 目的
survey / interview 実行時の質問定義を構造化する。

### 4.2 必須フィールド

- `prompt_spec_id`
- `mode`
- `instructions`
- `questions`
- `output_schema_hint`
- `metadata`


### 4.3 フィールド仕様

#### `prompt_spec_id`

- 型: string

#### `mode`

- 型: string
- 例:

- `"survey"`
- `"interview_single_turn"`
- `"interview_multi_turn"`



#### `instructions`

- 型: array[string]
- 説明:

- synthetic agent であること
- 根拠不足時は保留すること
- JSON で返すこと
- 実在人物を装わないこと



#### `questions`

- 型: array[object]
- 各 question object の最低限:

- `question_id`
- `text`
- `type`
- `required`



#### `output_schema_hint`

- 型: object
- 説明: expected JSON keys を示す

#### `metadata`

- 型: object


### 4.4 question object 例

- `question_id`: string
- `text`: string
- `type`: string

- `"likert"`
- `"open_text"`
- `"single_choice"`
- `"multi_choice"`
- `"numeric_estimate"`


- `required`: boolean
- `scale`: object | null
- `choices`: array[string] | null


### 4.5 MVP 最小例

```json
{
  "prompt_spec_id": "supermarket-launch-survey-v1",
  "mode": "survey",
  "instructions": [
    "あなたは実在人物ではなく、synthetic consumer agent として応答してください。",
    "与えられた agent profile と context に基づいて答えてください。",
    "根拠が不足する場合は uncertainty を上げてください。",
    "JSON 形式で返答してください。"
  ],
  "questions": [
    {
      "question_id": "q1",
      "text": "この商品を試してみたいと思いますか？",
      "type": "likert",
      "required": true
    },
    {
      "question_id": "q2",
      "text": "気になる点や買わない理由があれば教えてください。",
      "type": "open_text",
      "required": true
    }
  ],
  "output_schema_hint": {
    "purchase_intent": "1-5",
    "reasons": "array[string]",
    "objections": "array[string]",
    "confidence": "low|medium|high"
  },
  "metadata": {
    "version": "0.1"
  }
}
```

### 4.6 バリデーション方針

- questions は最低1件
- instructions は空にしない
- mode は制限付き enum 推奨
- output keys は後続 parser と整合させる


## 5. Aggregated Output Schema

### 5.1 目的
agent 単位の回答を集約した結果を保存する。

### 5.2 必須フィールド

- `aggregation_id`
- `scenario_id`
- `population_id`
- `summary`
- `segment_summaries`
- `metrics`
- `uncertainty_summary`
- `metadata`


### 5.3 フィールド仕様

#### `aggregation_id`

- 型: string

#### `scenario_id`

- 型: string

#### `population_id`

- 型: string

#### `summary`

- 型: object
- 最低限:

- `overall_takeaway`
- `top_reasons`
- `top_objections`



#### `segment_summaries`

- 型: array[object]
- 各要素の推奨キー:

- `segment_key`
- `segment_label`
- `takeaway`
- `sample_size`
- `purchase_intent_distribution`
- `top_reasons`
- `top_objections`



#### `metrics`

- 型: object
- 例:

- `mean_purchase_intent`
- `high_interest_ratio`
- `price_sensitivity_summary`
- `channel_preference_summary`



#### `uncertainty_summary`

- 型: object
- 例:

- `overall_uncertainty`
- `high_disagreement_segments`
- `low_evidence_areas`



#### `citation_summary`

- 型: array[object] | null

#### `metadata`

- 型: object


### 5.4 MVP 最小例

```json
{
  "aggregation_id": "agg-001",
  "scenario_id": "tokyo-supermarket-launch-001",
  "population_id": "tokyo-mvp-v1",
  "summary": {
    "overall_takeaway": "単身・共働き層で関心が高いが、価格上昇で継続利用に懸念がある",
    "top_reasons": ["健康的", "時短になる"],
    "top_objections": ["価格が高い", "量が少ない可能性"]
  },
  "segment_summaries": [],
  "metrics": {
    "mean_purchase_intent": 3.6
  },
  "uncertainty_summary": {
    "overall_uncertainty": "medium"
  },
  "metadata": {
    "generated_at": "2026-06-22T10:00:00Z"
  }
}
```

### 5.5 バリデーション方針

- summary は必須
- metrics は数値・カテゴリ混在可
- uncertainty_summary は省略不可
- segment は MVP では空配列可


## 6. Demand Estimation Output Schema

### 6.1 目的
scenario-based な demand / inventory suggestion を区間付きで表す。

### 6.2 必須フィールド

- `estimation_id`
- `scenario_id`
- `input_ref`
- `ranges`
- `assumptions`
- `risk_factors`
- `confidence`
- `metadata`


### 6.3 フィールド仕様

#### `estimation_id`

- 型: string

#### `scenario_id`

- 型: string

#### `input_ref`

- 型: object
- 例:

- `aggregation_id`
- `population_id`



#### `ranges`

- 型: object
- 必須キー:

- `conservative`
- `base`
- `optimistic`



各 range の型:

- `lower`: number
- `upper`: number
- `unit`: string

#### `assumptions`

- 型: array[string]

#### `risk_factors`

- 型: array[string]

#### `segment_sensitivity`

- 型: array[object] | null

#### `confidence`

- 型: string
- 例:

- `"low"`
- `"medium"`
- `"high"`



#### `warnings`

- 型: array[string] | null

#### `metadata`

- 型: object


### 6.4 MVP 最小例

```json
{
  "estimation_id": "demand-001",
  "scenario_id": "tokyo-supermarket-launch-001",
  "input_ref": {
    "aggregation_id": "agg-001",
    "population_id": "tokyo-mvp-v1"
  },
  "ranges": {
    "conservative": {
      "lower": 600,
      "upper": 800,
      "unit": "units_per_period"
    },
    "base": {
      "lower": 900,
      "upper": 1200,
      "unit": "units_per_period"
    },
    "optimistic": {
      "lower": 1300,
      "upper": 1700,
      "unit": "units_per_period"
    }
  },
  "assumptions": [
    "初期販促は限定的",
    "健康訴求が一定程度伝わる"
  ],
  "risk_factors": [
    "価格感度が高い層で継続利用不確実",
    "実データ校正がまだ不十分"
  ],
  "confidence": "medium",
  "metadata": {
    "generated_at": "2026-06-22T10:00:00Z"
  }
}
```

### 6.5 バリデーション方針

- lower <= upper
- conservative <= base <= optimistic を推奨（厳密必須ではないが整合判定可能）
- confidence は enum 化推奨
- assumptions を必須にする


## 7. Evaluation Record Schema

### 7.1 目的
evaluation / calibration の記録を残す。

### 7.2 必須フィールド

- `evaluation_id`
- `target_type`
- `target_ref`
- `metrics`
- `findings`
- `metadata`


### 7.3 フィールド仕様

#### `evaluation_id`

- 型: string

#### `target_type`

- 型: string
- 例:

- `"population"`
- `"scenario_run"`
- `"aggregation"`
- `"demand_estimation"`



#### `target_ref`

- 型: object

#### `metrics`

- 型: object
- 例:

- `representativeness_score`
- `stability_score`
- `evidence_coverage_score`
- `bias_risk_level`



#### `findings`

- 型: array[string]

#### `calibration_recommendations`

- 型: array[string] | null

#### `benchmark_refs`

- 型: array[string] | null

#### `metadata`

- 型: object


### 7.4 MVP 最小例

```json
{
  "evaluation_id": "eval-001",
  "target_type": "population",
  "target_ref": {
    "population_id": "tokyo-mvp-v1"
  },
  "metrics": {
    "representativeness_score": 0.72,
    "stability_score": 0.65,
    "evidence_coverage_score": 0.68
  },
  "findings": [
    "単身層に比重がやや寄っている",
    "地域差を十分に表現できていない可能性がある"
  ],
  "metadata": {
    "generated_at": "2026-06-22T10:00:00Z"
  }
}
```

### 7.5 バリデーション方針

- target_type は enum 推奨
- metrics は数値・カテゴリ混在可
- findings は最低1件推奨


## 8. Provenance / Citation Trace Schema

### 8.1 目的
RAG や集約結果における典拠・出所・参照経路を保持する。

### 8.2 必須フィールド

- `trace_id`
- `source_ref`
- `used_in`
- `citation_text`
- `metadata`


### 8.3 フィールド仕様

#### `trace_id`

- 型: string

#### `source_ref`

- 型: object
- 例:

- `datasource_id`
- `document_id`
- `chunk_id`



#### `used_in`

- 型: object
- 例:

- `agent_id`
- `scenario_id`
- `response_id`



#### `citation_text`

- 型: string
- 説明: 実際の引用文そのもの、または要約

#### `relevance_score`

- 型: number | null

#### `metadata`

- 型: object
- 例:

- `retrieved_at`
- `retrieval_method`
- `region_filter`
- `category_filter`




### 8.4 MVP 最小例

```json
{
  "trace_id": "trace-001",
  "source_ref": {
    "datasource_id": "sample-market-note-001",
    "document_id": "doc-001",
    "chunk_id": "chunk-003"
  },
  "used_in": {
    "agent_id": "tokyo-agent-0001",
    "scenario_id": "tokyo-supermarket-launch-001",
    "response_id": "resp-0001"
  },
  "citation_text": "都市部単身層では時短・健康訴求の冷凍食品に一定の受容余地がある",
  "relevance_score": 0.82,
  "metadata": {
    "retrieved_at": "2026-06-22T10:00:00Z",
    "retrieval_method": "vector_search",
    "region_filter": "tokyo-metropolitan",
    "category_filter": "frozen_food"
  }
}
  ```

  ## 9. スキーマ間の関係

  ```text
  datasource metadata
    -> normalized corpus
      -> provenance / citation trace
        -> agent grounding context
          -> survey/interview response
            -> aggregated output
              -> demand estimation
                -> evaluation record
  ```

  さらに:

  ```text
  population config
    -> synthetic agent schema
      -> scenario target selection
        -> per-agent execution
  ```

  ## 10. 今後 schemas/ 配下に作るべき JSON Schema 一覧

  最低限、以下を作る。

  - `schemas/agent.schema.json`
  - `schemas/datasource.schema.json`
  - `schemas/scenario.schema.json`
  - `schemas/prompt_spec.schema.json`
  - `schemas/aggregation.schema.json`
  - `schemas/demand_estimation.schema.json`
  - `schemas/evaluation.schema.json`
  - `schemas/provenance_trace.schema.json`

将来的には以下も追加可能。

  - `schemas/population_config.schema.json`
  - `schemas/model_request.schema.json`
  - `schemas/model_response.schema.json`
  - `schemas/run_metadata.schema.json`


  ## 11. Pydantic モデル対応方針

  推奨ファイル配置:

  - `agents/models.py`
  - `rag/models.py`
  - `simulations/models.py`
  - `evaluation/models.py`
  - `core/models.py`


配置の目安


  ### `agents/models.py`

  - SyntheticConsumerAgent
  - PopulationConfig（将来）
  - AgentConstraints
  - ResponseStyle
  - UncertaintyProfile



  ### `rag/models.py`

  - DataSourceMetadata
  - CitationTrace
  - RetrievedChunk
  - GroundingContext



  ### `simulations/models.py`

  - Scenario
  - PromptSpec
  - AggregatedOutput
  - DemandEstimationOutput



  ### `evaluation/models.py`

  - EvaluationRecord




  ## 12. 実装優先順位

  推奨順:

  1. `agent.schema.json`
  2. `scenario.schema.json`
  3. `datasource.schema.json`
  4. `prompt_spec.schema.json`
  5. `aggregation.schema.json`
  6. `demand_estimation.schema.json`
  7. `evaluation.schema.json`
  8. `provenance_trace.schema.json`

理由:

  - まず population / scenario / data source がないとパイプラインの形が決まらない
  - aggregation / estimation / evaluation は後続で乗る

  ## 13. テスト方針

  各 schema について最低限以下を用意する。

  ### 13.1 正常系テスト

  - MVP最小例が validation を通る

  ### 13.2 異常系テスト

  - 必須フィールド欠損
  - enum 不正値
  - 数値範囲違反
  - 空配列禁止フィールド違反

  ### 13.3 将来の追加テスト

  - backward compatibility
  - migration tests
  - sample scenario end-to-end schema consistency test


  ## 14. 安全・倫理上の注意を schema にどう反映するか
スキーマはただの技術定義ではなく、危険な実装を抑制する制約装置でもある。
具体策

  - SyntheticConsumerAgent に personal identity を持ち込まない
  - DataSourceMetadata に license / allowed_use を必須化する
  - PromptSpec に synthetic role の instruction を強制しやすい構造を持たせる
  - DemandEstimationOutput に assumptions / warnings / confidence を必須化する
  - EvaluationRecord に未校正点を残しやすくする


  ## 15. 最終メモ
本プロジェクトにおける schema は、単なる serialization 仕様ではない。
それは、

  - 安全性
  - provenance
  - 再現性
  - 実装容易性
  - 将来拡張性
  - 評価可能性

を支える**設計契約（design contract）**である。
後続の JSON Schema / Pydantic 実装では、本書を元に:

  - enum 整備
  - description 追加
  - example 追加
  - strict validation
  - versioning

を段階的に強化していく。

