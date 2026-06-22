"""Compatibility facade for shared domain models.

The real implementations now live in agents.models, rag.models,
simulations.models, and evaluation.models, following the structure described in
docs/schema-spec.md.
"""

from agents.models import (
    AgentConstraints as Constraints,
    AgentMetadata,
    ChannelPreference,
    ConfidenceLevel,
    MemoryEntry,
    PriceSensitivity,
    ResponseStyle,
    SyntheticConsumerAgent,
    UncertaintyProfile,
)
from evaluation.models import EvaluationRecord
from rag.models import CitationTrace, DataSourceMetadata as DatasourceMetadata, Provenance
from simulations.models import (
    AggregatedOutput,
    DemandEstimationOutput,
    ProductOrService,
    ScenarioDefinition,
    ScenarioMetadata,
    TargetAgents,
)

ScenarioOutput = AggregatedOutput

__all__ = [
    "AggregatedOutput",
    "AgentMetadata",
    "ChannelPreference",
    "CitationTrace",
    "ConfidenceLevel",
    "Constraints",
    "DatasourceMetadata",
    "DemandEstimationOutput",
    "EvaluationRecord",
    "MemoryEntry",
    "PriceSensitivity",
    "ProductOrService",
    "Provenance",
    "ResponseStyle",
    "ScenarioDefinition",
    "ScenarioMetadata",
    "ScenarioOutput",
    "SyntheticConsumerAgent",
    "TargetAgents",
    "UncertaintyProfile",
]