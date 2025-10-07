# Three-Tier Intelligence Architecture Example

This example demonstrates implementing the **three-tier intelligent storage architecture** using Graphiti's custom entity and edge types. While the example uses restaurant data, the architecture is **domain-agnostic** and works across industries.

## Architecture Overview

The system processes business analysis reports into three performance-optimized storage tiers:

```
Cold Tier (Raw Data) → Warm Tier (Structured Metrics) → Hot Tier (Insights)
```

### Storage Tiers

| Tier | Node Types | Purpose | Performance |
|------|------------|---------|-------------|
| **Cold** | DataBatch, DataSlice | Raw ingested facts | Seconds-minutes |
| **Warm** | MetricDefinition, MetricSeries, MetricObservation | Structured business metrics | 100ms-1s |  
| **Hot** | Insight, Anomaly, Correlation | Pre-computed analysis | 10-100ms |

## Custom Node Types

### Cold Tier: Raw Data Storage
- **DataBatch**: Ingestion batch metadata
- **DataSlice**: Atomized facts at specific dimensions (entity + date + flexible dimensions)

### Warm Tier: Structured Metrics  
- **MetricDefinition**: Business metric schemas (covers, staffing ratios)
- **MetricSeries**: Logical time series for metric + dimensions
- **MetricObservation**: Individual measurement points
- **CompositeMetricDefinition**: Derived metrics (revenue per cover)

### Hot Tier: Intelligence Layer
- **Insight**: High-level business insights and patterns
- **Anomaly**: Statistical outliers and deviations  
- **Correlation**: Relationships between metric series

## Domain Flexibility

The architecture supports multiple business domains through flexible configuration:

- **Restaurant**: `entity_id="Aqueous"`, `dimensions={"meal_period": "breakfast", "day_type": "weekend"}`
- **E-commerce**: `entity_id="LAPTOP001"`, `dimensions={"channel": "online", "category": "electronics"}`  
- **Manufacturing**: `entity_id="FactoryA"`, `dimensions={"shift": "day", "product_line": "widgets"}`
- **Healthcare**: `entity_id="Ward3B"`, `dimensions={"department": "cardiology", "shift": "night"}`

See `domain_configs.py` for implementation examples across different industries.

## Custom Edge Types

### Data Flow Relationships
- **CREATED**: DataBatch → DataSlice
- **FEEDS**: DataSlice → MetricObservation
- **HAS_SERIES**: MetricDefinition → MetricSeries
- **HAS_OBSERVATION**: MetricSeries → MetricObservation

### Temporal Relationships  
- **NEXT**: MetricObservation → MetricObservation (time series chain)
- **ROLLS_UP_INTO**: Fine-grain → Aggregated observations
- **SUPERSEDED_BY**: Revision chains for corrections

### Analysis Relationships
- **GENERATES_INSIGHT**: MetricObservation → Insight
- **ABOUT_METRIC_SERIES**: Insight → MetricSeries
- **ON_OBSERVATION**: Anomaly → MetricObservation
- **BETWEEN**: Correlation → MetricSeries

### Composite Relationships
- **USES_METRIC**: CompositeMetricDefinition → MetricDefinition
- **DEFINES_SERIES**: CompositeMetricDefinition → MetricSeries  
- **DERIVED_FROM**: MetricObservation → MetricObservation

## Data Processing Example

The example processes `analysis_report.md` containing:

### Raw Data (Cold Tier)
```
DataBatch: "Analysis Report May 9-15, 2025"
├── DataSlice: "Peak, 2025-05-09, Breakfast, 349 covers"
├── DataSlice: "Peak, 2025-05-09, Lunch, 262 covers"  
└── DataSlice: "Peak, 2025-05-09, Dinner, 296 covers"
```

### Structured Metrics (Warm Tier)
```
MetricDefinition: "Total Guest Covers"
├── MetricSeries: "Covers for Aqueous+Breakfast"
│   ├── MetricObservation: "2025-05-09: 349 covers"
│   ├── MetricObservation: "2025-05-10: 465 covers" 
│   └── MetricObservation: "2025-05-11: 321 covers"
```

### Intelligence Layer (Hot Tier)  
```
Insight: "Weekend Staffing Premium Required"
├── Summary: "Weekend breakfast volumes exceed weekday by 83%"
├── Severity: "high" 
└── ABOUT_METRIC_SERIES → "Covers for Aqueous+Breakfast"

Anomaly: "Saturday Breakfast Volume Spike"  
├── Expected: 281 covers
├── Actual: 465 covers (+65% deviation)
└── ON_OBSERVATION → "2025-05-10 breakfast observation"
```

## Two Implementation Approaches

### 🏗️ Structured Approach (`report_parser.py`)
Uses predefined schemas and explicit metric definitions. Best for:
- Production systems with known business domains
- Regulatory compliance requirements  
- Performance-critical applications
- Consistent data structure needs

### 🧠 Autonomous Approach (`autonomous_parser.py`) 
Lets Graphiti's LLM discover entities and relationships autonomously. Best for:
- Exploratory data analysis
- Unknown or evolving data patterns
- Research and discovery scenarios
- Flexible content analysis

See `APPROACH_COMPARISON.md` for detailed comparison and hybrid strategies.

## Usage

### Installation
```bash
```bash
# Ensure Graphiti core is installed
cd examples/three_tier_architecture

# Option 1: Structured approach with predefined schemas
python report_parser.py

# Option 2: Autonomous approach with LLM discovery  
python autonomous_parser.py
```
```

### Running the Example
```bash
cd /Users/maxhuang/projects/llm/graphiti/examples/restaurant_analysis
python report_parser.py
```

### Expected Output
```
🧹 Clearing existing data for group_id: restaurant-analysis
📖 Reading analysis report: /path/to/analysis_report.md
📊 Parsed report with 7 daily records
🗄️  Creating Cold Tier: Raw data storage...
✅ Created DataBatch: analysis_report_20251003_143022  
✅ Created 21 DataSlice nodes
📈 Creating Warm Tier: Structured metrics...
✅ Created 6 MetricDefinition nodes
✅ Created 21 MetricObservation nodes
🧠 Creating Hot Tier: Insights and analysis...
✅ Created 3 Insight nodes
✅ Created 2 Anomaly nodes

📊 RESTAURANT ANALYSIS PARSING SUMMARY
==================================================
Group ID: restaurant-analysis
Data Batch: analysis_report_20251003_143022

📈 NODE COUNTS BY TYPE:
  Entity: 53
  Episodic: 53  
  MetricObservation: 21
  DataSlice: 21
  MetricDefinition: 6
  Insight: 3
  Anomaly: 2
  DataBatch: 1

💡 SAMPLE INSIGHTS GENERATED:
  1. Guest Volume Patterns Analysis (Severity: medium)
     Breakfast averages 281 covers, lunch 251, dinner 194. Peak volumes occur on weekends...
  2. Weekend Staffing Premium Required (Severity: high)  
     Weekend breakfast volumes exceed weekday by 83%, requiring 30-40% additional staffing...
  3. Dinner Service Complexity Analysis (Severity: medium)
     Dinner service requires highest staffing intensity (35-60 staff per 100 covers)...

⚠️  ANOMALIES DETECTED: 2

✅ Three-tier storage architecture successfully implemented!
   • Cold Tier: Raw data episodes and DataBatch/DataSlice nodes
   • Warm Tier: MetricDefinition/Series/Observation nodes
   • Hot Tier: Insight and Anomaly nodes
```

## Key Features Demonstrated

### 1. **Custom Entity Types**
- Domain-specific business objects (DataBatch, MetricObservation, Insight)
- Rich property schemas with validation
- Proper inheritance and composition patterns

### 2. **Custom Edge Types**  
- Semantic relationships with metadata
- Temporal chains and hierarchies
- Lineage tracking for explainability

### 3. **Three-Tier Performance Architecture**
- **Hot lookups**: Pre-computed insights for instant responses
- **Warm analysis**: Structured metrics for fast aggregation  
- **Cold discovery**: Raw episodes for deep pattern mining

### 4. **Multi-Modal Storage**
- Episodes for unstructured content and semantic search
- Structured nodes for precise queries and aggregations
- Hybrid approach maximizing both flexibility and performance

### 5. **Business Intelligence Pipeline**
- Automated insight generation from metric observations
- Statistical anomaly detection with confidence scores
- Relationship discovery between metrics and business outcomes

## Business Applications

This architecture enables:

### Operational Queries
- *"Why did staffing costs spike on Saturday?"* → Hot tier insight lookup
- *"What's the correlation between weather and covers?"* → Warm tier analysis  
- *"Find all mentions of staffing issues in reports"* → Cold tier episode search

### Predictive Analytics
- Anomaly detection triggers for operational alerts
- Pattern recognition for demand forecasting
- Metric correlation discovery for root cause analysis

### Compliance & Auditing  
- Full lineage from raw reports to business decisions
- Temporal chains showing metric evolution over time
- Revision tracking for data corrections and updates

## Extension Points

### Additional Custom Types
```python
# Forecasting capabilities
class Forecast(BaseModel):
    prediction_horizon: str
    confidence_interval: Tuple[float, float]
    model_type: str
    
# Event impact analysis  
class BusinessEvent(BaseModel):
    event_type: str  # holiday, weather, promotion
    impact_metrics: List[str]
    duration: timedelta
```

### Advanced Edge Types
```python
# Causal relationships
class CausesEdge(BaseModel):
    causality_confidence: float
    lag_effect: timedelta
    
# Forecasting relationships  
class PredictedByEdge(BaseModel):
    model_accuracy: float
    prediction_date: datetime
```

This example demonstrates how Graphiti's custom types enable building sophisticated, domain-specific knowledge graphs that bridge unstructured content with structured analytics.