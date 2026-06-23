"""Markdown reporting for aggregated outputs and demand estimation outputs."""

from __future__ import annotations

from pathlib import Path

from simulations.models import AggregatedOutput, DemandEstimationOutput


def build_markdown_report(output: AggregatedOutput) -> str:
    """Render a human-readable markdown report from an aggregated output bundle."""

    lines: list[str] = []
    lines.append(f"# Aggregation Report: {output.scenario_id}")
    lines.append("")
    lines.append("> This report is a structured simulation summary for hypothesis support. It should not be treated as deterministic market truth.")
    lines.append("")
    lines.append("## Overall Summary")
    lines.append("")
    lines.append(f"- Overall takeaway: {output.summary.overall_takeaway}")
    lines.append(f"- Top reasons: {', '.join(output.summary.top_reasons) or 'None'}")
    lines.append(f"- Top objections: {', '.join(output.summary.top_objections) or 'None'}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    if output.metrics.mean_purchase_intent is not None:
        lines.append(f"- Mean purchase intent: {output.metrics.mean_purchase_intent:.2f}")
    else:
        lines.append("- Mean purchase intent: N/A")
    if output.metrics.high_interest_ratio is not None:
        lines.append(f"- High interest ratio: {output.metrics.high_interest_ratio:.2%}")
    else:
        lines.append("- High interest ratio: N/A")
    lines.append(f"- Overall uncertainty: {output.uncertainty_summary.overall_uncertainty}")
    lines.append("")
    lines.append("## Segment Summaries")
    lines.append("")
    for segment in output.segment_summaries:
        lines.append(f"### {segment.segment_label}")
        lines.append(f"- Sample size: {segment.sample_size}")
        lines.append(f"- Takeaway: {segment.takeaway}")
        lines.append(f"- Top reasons: {', '.join(segment.top_reasons) or 'None'}")
        lines.append(f"- Top objections: {', '.join(segment.top_objections) or 'None'}")
        distribution = ", ".join(f"{score}:{ratio:.2f}" for score, ratio in segment.purchase_intent_distribution.items())
        lines.append(f"- Purchase intent distribution: {distribution}")
        lines.append("")

    lines.append("## Uncertainty And Evidence")
    lines.append("")
    lines.append(
        f"- High disagreement segments: {', '.join(output.uncertainty_summary.high_disagreement_segments) or 'None'}"
    )
    lines.append(f"- Low evidence areas: {', '.join(output.uncertainty_summary.low_evidence_areas) or 'None'}")
    lines.append(f"- Citation count: {len(output.citation_summary)}")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is intended for pre-research comparison, not for final business decisions in isolation.")
    lines.append("- Explanation traces and citations should be reviewed together with real-world data and domain expertise.")
    return "\n".join(lines)


def save_markdown_report(report_text: str, output_path: Path) -> Path:
    """Persist a markdown report to disk."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")
    return output_path


def build_demand_markdown_report(
    estimation: DemandEstimationOutput,
    inventory_suggestion: dict[str, dict[str, float]],
) -> str:
    """Render a human-readable markdown report for demand estimation output."""

    lines: list[str] = []
    lines.append(f"# Demand Estimation Report: {estimation.input_ref.aggregation_id}")
    lines.append("")
    lines.append("> This output is a scenario-based estimate, not a deterministic forecast.")
    lines.append("")
    lines.append("## Demand Ranges")
    lines.append("")
    for scenario_name, range_output in estimation.ranges.items():
        lines.append(
            f"- {scenario_name}: {range_output.lower:.2f} - {range_output.upper:.2f} {range_output.unit}"
        )
    lines.append("")
    lines.append("## Assumptions")
    lines.append("")
    for assumption in estimation.assumptions:
        lines.append(f"- {assumption}")
    lines.append("")
    lines.append("## Risk Factors")
    lines.append("")
    for risk in estimation.risk_factors:
        lines.append(f"- {risk}")
    lines.append("")
    lines.append("## Segment Sensitivity")
    lines.append("")
    for sensitivity in estimation.segment_sensitivity:
        lines.append(f"- {sensitivity.segment_key}: {sensitivity.note}")
    lines.append("")
    lines.append("## Inventory Suggestion")
    lines.append("")
    for scenario_name, suggestion in inventory_suggestion.items():
        lines.append(
            f"- {scenario_name}: suggested_min_stock={suggestion['suggested_min_stock']:.2f}, suggested_max_stock={suggestion['suggested_max_stock']:.2f}"
        )
    lines.append("")
    lines.append("## Confidence And Warnings")
    lines.append("")
    lines.append(f"- Confidence: {estimation.confidence}")
    for warning in estimation.warnings:
        lines.append(f"- {warning}")
    return "\n".join(lines)