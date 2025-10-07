"""
Generic Custom Node and Edge Types for Three-Tier Intelligent Storage

This module defines generic, reusable structured nodes and edges that implement
the three-tier intelligent storage architecture for any business domain.

Based on the design document's node types:
- DataBatch, DataSlice (Cold Tier)  
- MetricDefinition, MetricSeries, MetricObservation (Warm Tier)
- Insight, Anomaly, Correlation (Hot Tier)

DOMAIN FLEXIBILITY:
These types are domain-agnostic and can be used for:
- Restaurant Analysis: entity_id="Aqueous", dimensions={"meal_period": "breakfast"}
- E-commerce: entity_id="ProductID", dimensions={"category": "electronics", "channel": "online"}
- Manufacturing: entity_id="FactoryA", dimensions={"shift": "night", "product_line": "widgets"}
- Healthcare: entity_id="HospitalX", dimensions={"department": "emergency", "severity": "high"}

The flexible dimensions and attributes dictionaries allow domain-specific data
while maintaining a consistent structural foundation.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# =============================================================================
# COLD TIER: Raw Data Storage
# =============================================================================

class DataBatch(BaseModel):
    """Represents one ingestion batch of raw restaurant data."""
    
    batch_id: str = Field(..., description="Unique identifier for this data batch")
    arrived_at: datetime = Field(..., description="When this batch was ingested")
    source_type: str = Field(..., description="Type of source system (POS, staffing, weather)")
    source_description: str = Field(..., description="Detailed description of data source")
    record_count: int = Field(..., description="Number of records in this batch")


class DataSlice(BaseModel):
    """Atomized fact at specific dimensional granularity."""
    
    slice_id: str = Field(..., description="Unique identifier for this data slice")
    entity_id: str = Field(..., description="Primary entity identifier (restaurant, store, user, etc.)")
    date: str = Field(..., description="Business date (YYYY-MM-DD)")
    time_start: Optional[str] = Field(None, description="Period start time")  
    time_end: Optional[str] = Field(None, description="Period end time")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Dimensional attributes (meal_period, category, segment, etc.)")
    raw_attributes: Dict[str, Any] = Field(default_factory=dict, description="Raw measurement values")


# =============================================================================
# WARM TIER: Structured Metrics
# =============================================================================

class MetricDefinition(BaseModel):
    """Semantic definition of a business metric."""
    
    metric_id: str = Field(..., description="Unique metric identifier")
    name: str = Field(..., description="Human-readable metric name")
    unit: str = Field(..., description="Unit of measurement (covers, dollars, ratio)")
    metric_type: str = Field(..., description="'basic' or 'composite'")
    granularity: str = Field(..., description="Temporal granularity (daily, meal_period, hourly)")
    dimension_schema: List[str] = Field(default_factory=list, description="Required dimensions")
    description: str = Field(..., description="Detailed metric description")
    version: str = Field(default="1.0", description="Metric definition version")


class MetricSeries(BaseModel):
    """Logical time series for a metric at specific dimensional signature."""
    
    series_id: str = Field(..., description="Unique series identifier")
    metric_id: str = Field(..., description="Reference to MetricDefinition")
    dimensions_signature: str = Field(..., description="Serialized dimensions key")
    entity_id: str = Field(..., description="Primary entity identifier")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Dimensional context (category, segment, etc.)")
    granularity: str = Field(..., description="Time granularity for this series")


class MetricObservation(BaseModel):
    """Single measurement point in a metric time series."""
    
    observation_id: str = Field(..., description="Unique observation identifier")  
    series_id: str = Field(..., description="Reference to MetricSeries")
    value: float = Field(..., description="Measured value")
    time_start: datetime = Field(..., description="Observation period start")
    time_end: datetime = Field(..., description="Observation period end")
    confidence: float = Field(default=1.0, description="Confidence in measurement (0-1)")
    quality_flags: Dict[str, Any] = Field(default_factory=dict, description="Data quality indicators")
    revision: int = Field(default=1, description="Revision number for corrections")


# =============================================================================
# WARM TIER: Composite Metrics
# =============================================================================

class CompositeMetricDefinition(BaseModel):
    """Definition for metrics derived from other metrics."""
    
    composite_id: str = Field(..., description="Unique composite metric identifier")
    name: str = Field(..., description="Human-readable name") 
    formula_expression: str = Field(..., description="Mathematical expression using metric IDs")
    input_metrics: List[str] = Field(..., description="List of required input metric IDs")
    output_granularity: str = Field(..., description="Granularity of computed results")
    description: str = Field(..., description="What this composite metric represents")


# =============================================================================
# HOT TIER: Insights and Analysis
# =============================================================================

class Insight(BaseModel):
    """High-level business insight derived from data analysis."""
    
    insight_id: str = Field(..., description="Unique insight identifier")
    title: str = Field(..., description="Brief insight title")
    summary: str = Field(..., description="Detailed insight description")
    insight_type: str = Field(..., description="pattern, anomaly, correlation, prediction")
    severity: str = Field(..., description="low, medium, high, critical")
    confidence: float = Field(..., description="Confidence in insight (0-1)")
    created_at: datetime = Field(..., description="When insight was generated")
    expiry_at: Optional[datetime] = Field(None, description="When insight becomes stale")
    affected_metrics: List[str] = Field(default_factory=list, description="Metric IDs this insight relates to")
    business_impact: str = Field(..., description="Expected business impact")


class Anomaly(BaseModel):
    """Statistical anomaly detection result."""
    
    anomaly_id: str = Field(..., description="Unique anomaly identifier")
    observation_id: str = Field(..., description="MetricObservation that triggered anomaly")
    anomaly_type: str = Field(..., description="spike, drop, trend_break, seasonal")
    severity_score: float = Field(..., description="Anomaly severity (z-score or similar)")
    expected_value: float = Field(..., description="Expected value based on historical pattern")
    actual_value: float = Field(..., description="Actual observed value")
    delta_percent: float = Field(..., description="Percentage deviation from expected")
    detection_method: str = Field(..., description="Algorithm used for detection")
    created_at: datetime = Field(..., description="When anomaly was detected")


class Correlation(BaseModel):
    """Statistical correlation between metric series."""
    
    correlation_id: str = Field(..., description="Unique correlation identifier")
    series_a_id: str = Field(..., description="First metric series")
    series_b_id: str = Field(..., description="Second metric series")
    correlation_coefficient: float = Field(..., description="Pearson correlation coefficient (-1 to 1)")
    p_value: float = Field(..., description="Statistical significance")
    window_start: datetime = Field(..., description="Analysis window start")
    window_end: datetime = Field(..., description="Analysis window end")
    sample_size: int = Field(..., description="Number of observations analyzed")
    correlation_type: str = Field(..., description="positive, negative, lagged")
    lag_days: Optional[int] = Field(None, description="Lag in days if lagged correlation")


# =============================================================================
# EDGE TYPE DEFINITIONS
# =============================================================================

class CreatedEdge(BaseModel):
    """DataBatch created DataSlice relationship."""
    
    batch_timestamp: datetime = Field(..., description="When batch created the slice")
    processing_version: str = Field(default="1.0", description="Data processing version")


class FeedsEdge(BaseModel):  
    """DataSlice feeds into MetricObservation relationship."""
    
    contribution_weight: float = Field(default=1.0, description="How much this slice contributes")
    aggregation_method: str = Field(..., description="sum, avg, count, etc.")


class HasSeriesEdge(BaseModel):
    """MetricDefinition has MetricSeries relationship."""
    
    created_at: datetime = Field(..., description="When series was created")
    series_status: str = Field(default="active", description="active, deprecated, archived")


class HasObservationEdge(BaseModel):
    """MetricSeries has MetricObservation relationship."""
    
    sequence_number: int = Field(..., description="Order within the series")
    is_latest: bool = Field(default=False, description="Whether this is the latest observation")


class NextEdge(BaseModel):
    """Temporal chain between observations in a series."""
    
    time_gap_hours: float = Field(..., description="Hours between observations")
    is_continuous: bool = Field(default=True, description="Whether timeline is continuous")


class RollsUpIntoEdge(BaseModel):
    """Hierarchical aggregation relationship."""
    
    aggregation_level: str = Field(..., description="hour->day, day->week, etc.")
    rollup_method: str = Field(..., description="sum, avg, max, etc.")


class SupersededByEdge(BaseModel):
    """Revision chain for corrected observations."""
    
    correction_reason: str = Field(..., description="Why the correction was made")
    corrected_at: datetime = Field(..., description="When correction was applied")


class GeneratesInsightEdge(BaseModel):
    """MetricObservation generated Insight relationship."""
    
    trigger_threshold: Optional[float] = Field(None, description="Value that triggered insight")
    analysis_method: str = Field(..., description="Algorithm or process used")


class UsesMetricEdge(BaseModel):
    """CompositeMetricDefinition uses MetricDefinition relationship."""
    
    formula_role: str = Field(..., description="Role in formula (numerator, denominator, etc.)")
    weight: float = Field(default=1.0, description="Weight in composite calculation")


class DefinesSeriesEdge(BaseModel):
    """CompositeMetricDefinition defines output MetricSeries."""
    
    output_binding: str = Field(..., description="How composite output maps to series")


class DerivedFromEdge(BaseModel):
    """MetricObservation derived from other observations."""
    
    derivation_method: str = Field(..., description="Calculation method used")
    input_weight: float = Field(default=1.0, description="Weight of input in derivation")


class AboutMetricSeriesEdge(BaseModel):
    """Insight is about MetricSeries relationship."""
    
    relevance_score: float = Field(..., description="How relevant insight is to series (0-1)")


class OnObservationEdge(BaseModel):
    """Anomaly detected on MetricObservation relationship."""
    
    detection_confidence: float = Field(..., description="Confidence in anomaly detection (0-1)")


class BetweenEdge(BaseModel):
    """Correlation between MetricSeries relationship."""
    
    correlation_strength: str = Field(..., description="weak, moderate, strong")
    statistical_significance: bool = Field(..., description="Whether correlation is significant")