# Discussion Summary — Simplification of Graph Understanding System

## 1. Core Clarifications
- The **Hot/Warm/Cold tiers are conceptual**, not physical databases.  
  - **Cold:** Actual data in ClickHouse, Redshift, or Spark.  
  - **Warm:** Aggregated metrics (daily/weekly facts).  
  - **Hot:** Insights and reasoning results in the graph.
- The **graph is not a time-series database** — it’s a **semantic cache** for relationships, lineage, and reasoning.
- The **MetricObservation** represents **semantic facts**, not raw timestamps.  
  Example: “May 3 breakfast covers = 340” rather than a time-series point.

---

## 2. Simplification Principles
1. **Decouple layers:** Understanding (graph) vs infrastructure (data engines) vs interaction (agents).  
2. **Flatten the model:** Start with 4–5 essential node types and minimal edge types.  
3. **Temporal model simplification:** Represent time as metadata in observations; add trend/seasonality nodes later.  
4. **Unified retrieval:** One traversal from metric → observation → insight.  
5. **No physical tiers:** Use logical tiering (attribute flags) until scale demands caching.  
6. **Add complexity only when needed:** Correlation, composite metrics, rollups, or caching should be incremental.

---

## 3. Simplified Architecture Overview
### Core Node Types
- **DataSource** — Pointer to external data.  
- **MetricDefinition** — Defines metric meaning.  
- **MetricObservation** — Aggregated metric instance.  
- **Insight** — Derived understanding.  
- **TimePeriod** — Optional grouping.

### Core Edge Types
- `FEEDS` — DataSource → MetricObservation  
- `DERIVED_FROM` — MetricObservation → MetricObservation  
- `GENERATES_INSIGHT` — MetricObservation → Insight  
- `CONTAINS` — TimePeriod → MetricObservation  

---

## 4. Design Philosophy
| Principle | Description |
|------------|-------------|
| **Understanding over storage** | Graph holds reasoning, not data |
| **Semantic identity** | `MetricSeries` or `MetricDefinition` keeps stable meaning |
| **Progressive complexity** | Start lean, evolve when justified |
| **Temporal reasoning as metadata** | No early need for trend or window nodes |
| **Reasoning density before scale** | Focus on quality of relationships before optimization |

---

## 5. Next Steps
- Document this MVP as “Phase 1 Simplified Design.”  
- Implement minimal schema and single traversal query path.  
- Delay composite metric DAG and caching layers until system shows reasoning stability.  
- Later phases can reintroduce advanced features (`CompositeMetricDefinition`, `Anomaly`, `Correlation`, etc.) incrementally.
