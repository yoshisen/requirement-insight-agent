"""Evaluation and calibration helpers for the MVP."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.metrics import (
    bias_risk_level,
    evidence_coverage_score,
    representativeness_score,
    stability_score,
    summarize_agent_distribution,
)
from evaluation.models import EvaluationMetadata, EvaluationMetrics, EvaluationRecord, UncertaintyMonitoring
from agents.population import PopulationBuildResult
from simulations.models import AggregatedOutput


def load_population_result(path: Path) -> PopulationBuildResult:
    """Load a saved population build result."""

    return PopulationBuildResult.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_aggregated_output(path: Path) -> AggregatedOutput:
    """Load a saved aggregated output."""

    return AggregatedOutput.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_expected_distribution(path: Path) -> dict[str, dict[str, float]]:
    """Load expected benchmark distributions from JSON."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["dimensions"]


def evaluate_artifacts(
    *,
    population: PopulationBuildResult,
    aggregated: AggregatedOutput,
    benchmark_path: Path,
    comparison_output: AggregatedOutput | None = None,
) -> EvaluationRecord:
    """Build an MVP evaluation record from population and aggregate outputs."""

    actual_distribution = summarize_agent_distribution(population)
    expected_distribution = load_expected_distribution(benchmark_path)
    repr_score, repr_detail, uncalibrated = representativeness_score(actual_distribution, expected_distribution)
    stable_score, stable_detail = stability_score(aggregated, comparison_output)
    evidence_score = evidence_coverage_score(aggregated)
    bias_level = bias_risk_level(aggregated)

    findings = _build_findings(repr_score, stable_score, evidence_score, bias_level, uncalibrated)
    recommendations = _build_recommendations(uncalibrated, aggregated)

    return EvaluationRecord(
        evaluation_id=f"eval-{aggregated.output_id}",
        target_type="aggregation",
        target_ref={
            "aggregation_id": aggregated.output_id,
            "population_id": population.population_id,
            "scenario_id": aggregated.scenario_id,
        },
        metrics=EvaluationMetrics(
            representativeness_score=repr_score,
            stability_score=stable_score,
            evidence_coverage_score=evidence_score,
            bias_risk_level=bias_level,
            representativeness_detail=repr_detail,
            stability_detail=stable_detail,
        ),
        findings=findings,
        calibration_recommendations=recommendations,
        benchmark_refs=[str(benchmark_path)],
        uncalibrated_areas=uncalibrated,
        uncertainty_monitoring=UncertaintyMonitoring(
            overall_uncertainty=aggregated.uncertainty_summary.overall_uncertainty,
            disagreement_signals=aggregated.uncertainty_summary.high_disagreement_segments,
        ),
        citation_summary=aggregated.citation_summary,
        metadata=EvaluationMetadata(
            generated_at=aggregated.metadata.generated_at,
            evaluator_version="0.1.0",
            notes="MVP evaluation placeholder generated from current synthetic population and aggregated output.",
        ),
    )


def save_evaluation_record(record: EvaluationRecord, output_path: Path) -> Path:
    """Persist an evaluation record JSON file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def build_evaluation_markdown_report(record: EvaluationRecord) -> str:
    """Render a concise markdown report from an evaluation record."""

    lines: list[str] = []
    lines.append(f"# Evaluation Report: {record.evaluation_id}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    if record.metrics.representativeness_score is not None:
        lines.append(f"- Representativeness score: {record.metrics.representativeness_score:.2f}")
    if record.metrics.stability_score is not None:
        lines.append(f"- Stability score: {record.metrics.stability_score:.2f}")
    if record.metrics.evidence_coverage_score is not None:
        lines.append(f"- Evidence coverage score: {record.metrics.evidence_coverage_score:.2f}")
    lines.append(f"- Bias risk level: {record.metrics.bias_risk_level}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    for finding in record.findings:
        lines.append(f"- {finding}")
    lines.append("")
    lines.append("## Calibration Recommendations")
    lines.append("")
    for recommendation in record.calibration_recommendations:
        lines.append(f"- {recommendation}")
    lines.append("")
    lines.append("## Uncalibrated Areas")
    lines.append("")
    lines.append(f"- {', '.join(record.uncalibrated_areas) or 'None'}")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This evaluation is an MVP calibration scaffold and should be expanded with real-world benchmarks over time.")
    return "\n".join(lines)


def save_evaluation_markdown(report_text: str, output_path: Path) -> Path:
    """Persist an evaluation markdown report."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")
    return output_path


def _build_findings(
    repr_score: float,
    stable_score: float,
    evidence_score: float,
    bias_level: str,
    uncalibrated: list[str],
) -> list[str]:
    findings = [
        f"Representativeness score is {repr_score:.2f}.",
        f"Stability score is {stable_score:.2f}.",
        f"Evidence coverage score is {evidence_score:.2f}.",
        f"Bias risk is currently assessed as {bias_level}.",
    ]
    if uncalibrated:
        findings.append("Uncalibrated dimensions remain: " + ", ".join(uncalibrated) + ".")
    return findings


def _build_recommendations(uncalibrated: list[str], aggregated: AggregatedOutput) -> list[str]:
    recommendations = []
    for dimension in uncalibrated:
        recommendations.append(f"Review and recalibrate the {dimension} distribution against stronger benchmark data.")
    if aggregated.uncertainty_summary.high_disagreement_segments:
        recommendations.append(
            "Investigate disagreement in segments: "
            + ", ".join(aggregated.uncertainty_summary.high_disagreement_segments)
            + "."
        )
    if aggregated.uncertainty_summary.low_evidence_areas:
        recommendations.append(
            "Strengthen evidence coverage for: "
            + ", ".join(aggregated.uncertainty_summary.low_evidence_areas)
            + "."
        )
    if not recommendations:
        recommendations.append("Expand calibration with stronger benchmarks and real survey comparisons as they become available.")
    return recommendations