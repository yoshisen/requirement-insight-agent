# Tokyo Supermarket Launch Example

この example は、東京圏のスーパーで高たんぱく低糖質の冷凍惣菜シリーズを上市するケースを想定した最小 scenario です。

用途:

- schema validation の入力例
- scenario execution の smoke input
- docs と code の整合チェック

## Files

- `scenario.json`: sample scenario definition
- `retrieval_query.json`: sample retrieval test query
- `product_brief.md`: product-side summary
- `research_questions.md`: research questions for the scenario
- `survey_prompt.sample.json`: survey prompt sample
- `interview_prompt.sample.json`: interview prompt sample
- `example_config.json`: end-to-end workflow config
- `run_example.ps1`: sample run script
- `expected_artifacts.md`: expected outputs after a full run

## Example Run

```powershell
ria run-example --config examples/tokyo-supermarket-launch/example_config.json --prompt-kind survey --output-dir .local/examples/tokyo-supermarket-launch
```