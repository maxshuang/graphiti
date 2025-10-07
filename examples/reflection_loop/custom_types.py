#!/usr/bin/env python3
"""
Simplified Custom Types for Graph-Based Understanding Layer with Reflection Loop

Based on simplified_design_doc_with_reflection_loop.md - focuses on core concepts:
- DataSource: Pointer to external data (Cold Tier)
- MetricDefinition: Defines measurable concept (semantic contract)  
- MetricObservation: Aggregated metric for time window (Warm Tier)
- Insight: Interpreted conclusion (Hot Tier)
- TimePeriod: Optional temporal grouping

The reflection loop enables continuous insight discovery and graph self-growth.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# CORE NODE TYPES - Simplified Schema
# =============================================================================

class DataSource(BaseModel):
    """Pointer to external data system (Cold Tier)"""
    source_id: str = Field(description="Unique identifier for this data source")
    source_type: str = Field(description="Type: file, database, api, stream")
    connection_string: str = Field(description="How to access this source")
    data_schema: Dict[str, Any] = Field(description="Expected data structure")
    source_last_updated: datetime = Field(description="When source was last accessed")  # Renamed to avoid conflicts


class MetricDefinition(BaseModel):
    """Defines a measurable concept - semantic contract"""
    metric_id: str = Field(description="Unique metric identifier")
    metric_name: str = Field(description="Human-readable metric name")
    unit: str = Field(description="Unit of measurement")
    calculation_method: str = Field(description="How this metric is calculated")
    business_context: str = Field(description="What this means for the business")
    dimensions: List[str] = Field(description="Expected dimensional breakdown")


class MetricObservation(BaseModel):
    """Aggregated metric value for a time window (Warm Tier)"""
    observation_id: str = Field(description="Unique observation identifier")
    metric_id: str = Field(description="Which metric this observes")
    dimensions: Dict[str, Any] = Field(description="Dimensional context")
    time_start: datetime = Field(description="Period start time")
    time_end: datetime = Field(description="Period end time") 
    period_label: str = Field(description="Human-readable period: 2025-W18")
    value: float = Field(description="The measured value")
    confidence: float = Field(default=1.0, description="Confidence in measurement")


class Insight(BaseModel):
    """Interpreted or generated conclusion (Hot Tier)"""
    insight_id: str = Field(description="Unique insight identifier")
    insight_type: str = Field(description="pattern, anomaly, correlation, trend")
    insight_summary: str = Field(description="Human-readable insight summary")  # Renamed from 'summary'
    confidence_score: float = Field(description="Statistical confidence")
    business_impact: str = Field(description="Potential business impact")
    insight_generated_at: datetime = Field(description="When insight was created")  # Renamed from generated_at to avoid conflicts
    generation_method: str = Field(description="How insight was derived")


class TimePeriod(BaseModel):
    """Optional temporal grouping for reasoning"""
    period_id: str = Field(description="Unique period identifier")
    period_type: str = Field(description="day, week, month, quarter, year")
    period_label: str = Field(description="Human readable: 2025-W18, May 2025")
    period_start: datetime = Field(description="Period start timestamp")
    period_end: datetime = Field(description="Period end timestamp")
    observation_count: int = Field(default=0, description="Observations in period")


# =============================================================================
# REFLECTION LOOP NODES - For Continuous Discovery
# =============================================================================

class MetaInsight(BaseModel):
    """Generalized insight discovered through reflection loop"""
    meta_insight_id: str = Field(description="Unique meta-insight identifier")
    pattern_description: str = Field(description="Generalized pattern observed")
    occurrence_count: int = Field(description="How many times pattern seen")
    meta_first_observed: datetime = Field(description="When pattern first detected")  # Renamed to avoid conflicts
    meta_last_observed: datetime = Field(description="Most recent occurrence")  # Renamed to avoid conflicts
    confidence_level: str = Field(description="low, medium, high")


class InsightCluster(BaseModel):
    """Group of similar insights discovered by reflection loop"""
    cluster_id: str = Field(description="Unique cluster identifier")
    cluster_theme: str = Field(description="Common theme across insights")
    insight_count: int = Field(description="Number of insights in cluster")
    similarity_threshold: float = Field(description="Similarity threshold used")
    cluster_created_at: datetime = Field(description="When cluster was formed")  # Renamed from created_at


# =============================================================================
# EDGE TYPES - Core Relationships
# =============================================================================

class FeedsEdge(BaseModel):
    """DataSource → MetricObservation: Observation computed from data"""
    data_lineage: str = Field(description="How observation derived from source")
    extraction_method: str = Field(description="ETL process or calculation")
    data_quality: float = Field(default=1.0, description="Quality score 0-1")


class DerivedFromEdge(BaseModel):
    """MetricObservation → MetricObservation: Derived metric lineage"""
    derivation_formula: str = Field(description="How target derived from source")
    transformation_type: str = Field(description="aggregation, calculation, etc")


class GeneratesInsightEdge(BaseModel):
    """MetricObservation → Insight: Observation leads to insight"""
    analysis_method: str = Field(description="How insight was generated")
    statistical_significance: float = Field(description="Statistical confidence")
    contributing_factors: List[str] = Field(description="What contributed to insight")


class ContainsEdge(BaseModel):
    """TimePeriod → MetricObservation: Period contains observation"""
    temporal_coverage: float = Field(default=1.0, description="How much of period covered")
    aggregation_method: str = Field(description="sum, avg, max, min, point")


class AboutMetricEdge(BaseModel):
    """Insight → MetricDefinition: Insight provides context for metric"""
    relevance_score: float = Field(description="How relevant insight is to metric")
    impact_type: str = Field(description="positive, negative, neutral")


# =============================================================================
# REFLECTION LOOP EDGES - For Continuous Discovery
# =============================================================================

class SimilarToEdge(BaseModel):
    """Insight → Insight: Semantic similarity discovered by reflection"""
    similarity_score: float = Field(description="Cosine similarity or other metric")
    similarity_method: str = Field(description="embedding, keywords, semantic")


class ConfirmsEdge(BaseModel):
    """Insight → Insight: One insight confirms another"""
    confirmation_strength: float = Field(description="How strongly it confirms")
    temporal_relationship: str = Field(description="before, after, concurrent")


class BelongsToEdge(BaseModel):
    """Insight → InsightCluster: Insight belongs to cluster"""
    cluster_assignment_score: float = Field(description="How well it fits cluster")
    assignment_method: str = Field(description="clustering algorithm used")


class EvolvesIntoEdge(BaseModel):
    """InsightCluster → MetaInsight: Cluster evolves into generalized pattern"""
    abstraction_level: str = Field(description="specific, general, universal")
    pattern_confidence: float = Field(description="Confidence in generalization")


# =============================================================================
# COMPLETE TYPE MAPPINGS
# =============================================================================

# All node types for Graphiti
ENTITY_TYPES = {
    # Core Schema
    'DataSource': DataSource,
    'MetricDefinition': MetricDefinition, 
    'MetricObservation': MetricObservation,
    'Insight': Insight,
    'TimePeriod': TimePeriod,
    
    # Reflection Loop Extensions
    'MetaInsight': MetaInsight,
    'InsightCluster': InsightCluster,
}

# All edge types for Graphiti  
EDGE_TYPES = {
    # Core Relationships
    'FEEDS': FeedsEdge,
    'DERIVED_FROM': DerivedFromEdge,
    'GENERATES_INSIGHT': GeneratesInsightEdge,
    'CONTAINS': ContainsEdge,
    'ABOUT_METRIC': AboutMetricEdge,
    
    # Reflection Loop Relationships
    'SIMILAR_TO': SimilarToEdge,
    'CONFIRMS': ConfirmsEdge,
    'BELONGS_TO': BelongsToEdge,
    'EVOLVES_INTO': EvolvesIntoEdge,
}

# Edge type mapping - which node types can connect with which edges
EDGE_TYPE_MAP = {
    # Core Data Flow
    ('DataSource', 'MetricObservation'): ['FEEDS'],
    ('MetricObservation', 'MetricObservation'): ['DERIVED_FROM'],
    ('MetricObservation', 'Insight'): ['GENERATES_INSIGHT'],
    ('TimePeriod', 'MetricObservation'): ['CONTAINS'],
    ('Insight', 'MetricDefinition'): ['ABOUT_METRIC'],
    
    # Reflection Loop Relationships
    ('Insight', 'Insight'): ['SIMILAR_TO', 'CONFIRMS'],
    ('Insight', 'InsightCluster'): ['BELONGS_TO'],
    ('InsightCluster', 'MetaInsight'): ['EVOLVES_INTO'],
    
    # Cross-layer connections
    ('MetricDefinition', 'MetricObservation'): ['FEEDS'],
    ('DataSource', 'MetricDefinition'): ['FEEDS'],
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_observation_id(metric_id: str, dimensions: Dict[str, Any], period_label: str) -> str:
    """Generate consistent observation ID from components"""
    dims_str = "_".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
    return f"obs_{metric_id}_{dims_str}_{period_label}".replace(" ", "_").lower()


def create_period_label(period_type: str, timestamp: datetime) -> str:
    """Generate period label from type and timestamp"""
    if period_type == "day":
        return timestamp.strftime("%Y-%m-%d")
    elif period_type == "week":
        year, week, _ = timestamp.isocalendar()
        return f"{year}-W{week:02d}"
    elif period_type == "month":
        return timestamp.strftime("%Y-%m")
    elif period_type == "quarter":
        quarter = (timestamp.month - 1) // 3 + 1
        return f"{timestamp.year}-Q{quarter}"
    elif period_type == "year":
        return str(timestamp.year)
    else:
        return timestamp.isoformat()


if __name__ == "__main__":
    # Test type creation
    print("🧩 Testing Simplified Custom Types...")
    
    # Test DataSource
    ds = DataSource(
        source_id="restaurant_pos_system",
        source_type="database",
        connection_string="postgres://pos.example.com/sales",
        data_schema={"covers": "int", "revenue": "float", "timestamp": "datetime"},
        last_updated=datetime.now()
    )
    print(f"✅ DataSource: {ds.source_id}")
    
    # Test MetricDefinition  
    md = MetricDefinition(
        metric_id="total_covers",
        metric_name="Total Guest Covers",
        unit="guest_count", 
        calculation_method="SUM(covers) GROUP BY restaurant, date",
        business_context="Daily guest volume indicator",
        dimensions=["restaurant", "meal_period", "date"]
    )
    print(f"✅ MetricDefinition: {md.metric_name}")
    
    # Test MetricObservation
    mo = MetricObservation(
        observation_id="obs_total_covers_restaurant=peak_2025-w18",
        metric_id="total_covers",
        dimensions={"restaurant": "Peak", "meal_period": "breakfast"},
        time_start=datetime(2025, 5, 3),
        time_end=datetime(2025, 5, 3, 23, 59),
        period_label="2025-05-03",
        value=340.0,
        confidence=0.95
    )
    print(f"✅ MetricObservation: {mo.value} {md.unit}")
    
    # Test Insight
    insight = Insight(
        insight_id="insight_weekend_spike_001",
        insight_type="pattern",
        summary="Weekend breakfast shows 43% higher covers than weekday average",
        confidence_score=0.87,
        business_impact="Potential staffing adjustment needed for weekends",
        generated_at=datetime.now(),
        generation_method="statistical_analysis"
    )
    print(f"✅ Insight: {insight.summary}")
    
    print(f"\n🚀 All types validated! Ready for reflection loop analysis.")