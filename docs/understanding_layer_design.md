# Understanding Layer — Generic Graph-Based System Design

## 1. Overview

This system is an **understanding layer** on top of evolving business data.
It uses a **graph database** to represent entities, metrics, lineage, and insights, allowing agents/LLMs to reason about data, derive new metrics, and detect anomalies.

---

## 2. Multi-Tier Storage Architecture

### Core Concept: Three-Tier Intelligent Storage
The system operates as a **multi-layered caching architecture** with three distinct storage tiers:

- **Hot Storage**: Pre-computed Insights, Anomalies, and Correlations - instant agent access (sub-100ms)
- **Warm Storage**: MetricObservations and MetricSeries - aggregated metrics for analysis (sub-second) 
- **Cold Storage**: Raw DataBatch/DataSlice nodes - full fidelity facts and undiscovered patterns (seconds to minutes)

### Agent Query Strategy
```mermaid
flowchart TD
  Query[Agent Query: Why did efficiency drop?]
  
  HotLookup[1. Check Hot Storage<br/>Existing Insights/Anomalies<br/>~10-100ms]
  
  HotFound{Found relevant<br/>insights?}
  
  WarmLookup[2. Check Warm Storage<br/>MetricObservations/Series<br/>~100ms-1s]
  
  WarmFound{Found sufficient<br/>metric context?}
  
  InstantResponse[3a. Return from<br/>pre-computed insights<br/>Ultra-fast response]
  
  WarmResponse[3b. Analyze warm metrics<br/>Generate new insights<br/>Fast response + cache update]
  
  ColdDig[3c. Dig into Cold Storage<br/>Analyze raw DataSlices<br/>Deep discovery + cache population]
  
  Query --> HotLookup
  HotLookup --> HotFound
  HotFound -->|Yes| InstantResponse
  HotFound -->|No| WarmLookup
  WarmLookup --> WarmFound
  WarmFound -->|Yes| WarmResponse
  WarmFound -->|No| ColdDig
  
  WarmResponse --> HotCache[Update Hot Cache]
  ColdDig --> WarmCache[Update Warm Cache]
  ColdDig --> HotCache
```

### Three-Tier Storage Mapping
| Tier | Node Types | Retention | Access Pattern | Performance |
|------|------------|-----------|----------------|-------------|
| **Hot** | Insight, Anomaly, Correlation | Indefinite (small volume) | Direct lookup by topic/metric | 10-100ms |
| **Warm** | MetricObservation, MetricSeries | 1-3 years | Traversal + time range queries | 100ms-1s |
| **Cold** | DataBatch, DataSlice | 90 days → archive | Full scan + ML analysis | Seconds-minutes |

### Storage Efficiency Principles
1. **Graduated Promotion**: Cold discovery → Warm aggregation → Hot insights
2. **Selective Materialization**: Only create Warm/Hot entries for actively queried patterns
3. **Cascading Invalidation**: New Cold data → invalidate Warm → regenerate Hot insights
4. **Background Warming**: ML pipelines pre-populate Warm/Hot tiers for high-value patterns

### Performance Benefits
- **Ultra-fast responses** (10-100ms) from Hot insights
- **Fast analysis** (100ms-1s) from Warm metrics when Hot insufficient  
- **Deep discovery** (seconds-minutes) from Cold storage when needed
- **Automatic cache promotion** of valuable patterns across tiers

---

## 3. Refined Layered Model (Addressing Data + Metric Evolution)

Your operational reality (multi-grain, multi-dimensional, derived + composite metrics) requires *three semantic layers* plus an operational/meta layer:

| Layer | Node Types | Purpose |
|-------|------------|---------|
| 0. Raw / Facts | DataBatch, DataSlice | Capture ingested mini-batches & normalized fact slices (e.g. (venue=Peak, date=2025-05-03, meal=BREAKFAST) covers=340) |
| 1. Metric Semantics | MetricDefinition, MetricSeries, MetricObservation | Define, identify, and store evolving metric time series (basic + composite) |
| 2. Derived Knowledge | CompositeMetricDefinition, Insight, Anomaly, Correlation | Higher-order reasoning outputs and interpretive artifacts |
| Ops / Lineage | Transformation, SourceFile (optional) | (Optional) external processing context if needed |

### 2.1 Core Node Types (Updated)
| Node | Key Props | Notes |
|------|-----------|-------|
| DataBatch | id, arrived_at, source_type | One ingestion unit (mini-batch) |
| DataSlice | id, dims:{restaurant, date, meal, role?}, time_start, time_end, raw_attrs:{} | Atomized fact at a grain |
| MetricDefinition | id, name, granularity, dimension_schema[], type ('basic'/'composite'), version | Semantic contract |
| MetricSeries | id (hash(def + dims signature)), dims_signature, granularity | Stable identity for a time series |
| MetricObservation | id, value, time_start, time_end, revision, quality:{...} | One point in a series |
| CompositeMetricDefinition | id, expression_dsl, output_granularity | Formula tree referencing MetricDefinitions |
| Insight | id, kind, severity, summary, created_at | Human / algorithm narrative anchor |
| Anomaly | id, zscore, expected, delta_pct | Specialized insight seed |
| Correlation | id, window, r_value, p_value | Relationship between series |

### 2.2 Edge Types (Updated)
| Edge | From → To | Purpose |
|------|-----------|---------|
| CREATED | DataBatch → DataSlice | Batch membership |
| FEEDS | DataSlice → MetricObservation | Raw fact contributes to observation |
| HAS_SERIES | MetricDefinition → MetricSeries | Definition → logical series |
| HAS_OBSERVATION | MetricSeries → MetricObservation | Series membership |
| NEXT | MetricObservation → MetricObservation | Temporal chain within a series |
| ROLLS_UP_INTO | MetricObservation → MetricObservation | Hierarchical temporal aggregation (day→week) |
| SUPERSEDED_BY | MetricObservation → MetricObservation | Revision lineage |
| GENERATES_INSIGHT | MetricObservation → Insight | Observation produced insight |
| USES_METRIC | CompositeMetricDefinition → MetricDefinition | Dependency graph (semantic) |
| DEFINES_SERIES | CompositeMetricDefinition → MetricSeries | Output binding |
| DERIVED_FROM | MetricObservation → MetricObservation | Fine-grain lineage (optional) |
| ABOUT_METRIC_SERIES | Insight → MetricSeries | Insight attachment |
| ON_OBSERVATION | Anomaly → MetricObservation | Anomaly target |
| BETWEEN | Correlation → MetricSeries | Correlated pair(s) |

---

## 4. Temporal & Hierarchical Linking
**Why NOT only timestamps?** We need fast window queries, revision handling, and rollups.

Mechanisms:
1. `:NEXT` provides an ordered singly-linked list per `MetricSeries` (fast recent traversal, incremental append).
2. `:ROLLS_UP_INTO` links fine-grain observations to their aggregates (e.g., each breakfast observation → that day aggregate → that week aggregate).
3. `:SUPERSEDED_BY` preserves correctness when late data arrives (agents ignore superseded nodes).
4. Optional materialized pointers: store `latest_obs_id` on `MetricSeries` for O(1) head fetch.

Mermaid (condensed):
```mermaid
graph TD
  MS[MetricSeries] --> O1[Obs t0]
  O1 -->|NEXT| O2[Obs t1]
  O2 -->|NEXT| O3[Obs t2]
  O1 -->|ROLLS_UP_INTO| D1[DayAgg]
  D1 -->|ROLLS_UP_INTO| W1[WeekAgg]
  O2 -->|SUPERSEDED_BY| O2r[Obs t1 rev2]
```

---

## 5. Composite Metric Mechanics
Composite definitions reference *definitions*, not observations. Runtime expands to current observations.

```mermaid
graph TD
  RevDef[MetricDefinition<br/>Total Revenue]
  CoversDef[MetricDefinition<br/>Total Covers]
  
  CompDef[CompositeMetricDefinition<br/>Revenue Per Cover<br/>formula: revenue/covers]
  
  RevSeries[MetricSeries<br/>Revenue for Peak]
  CoversSeries[MetricSeries<br/>Covers for Peak]
  CompSeries[MetricSeries<br/>RevPerCover for Peak]
  
  RevObs[MetricObservation<br/>May 1: $5000]
  CoversObs[MetricObservation<br/>May 1: 340 covers]
  CompObs[MetricObservation<br/>May 1: $14.71]
  
  CompDef -->|USES_METRIC| RevDef
  CompDef -->|USES_METRIC| CoversDef
  CompDef -->|DEFINES_SERIES| CompSeries
  
  RevDef -->|HAS_SERIES| RevSeries
  CoversDef -->|HAS_SERIES| CoversSeries
  
  RevSeries -->|HAS_OBSERVATION| RevObs
  CoversSeries -->|HAS_OBSERVATION| CoversObs
  CompSeries -->|HAS_OBSERVATION| CompObs
  
  CompObs -->|DERIVED_FROM| RevObs
  CompObs -->|DERIVED_FROM| CoversObs
```

Flow for computing a composite observation:
1. Resolve dependency DAG via `:USES_METRIC` edges.
2. For each dependency series, fetch aligned observations in target window.
3. Compute value; create new `MetricObservation` under the composite `MetricSeries`.
4. (Optional) Link via `:DERIVED_FROM` to source observations for explainability.
5. (Optional) Attach lightweight provenance properties on the observation itself (e.g. `ingestion_id`, `pipeline_label`).

Selective Recompute Trigger:
```
MATCH (md:MetricDefinition)<-[:USES_METRIC]-(cmp:CompositeMetricDefinition)
WHERE md.id IN $changed_basic_metrics
RETURN DISTINCT cmp;
```

---

## 6. Ingestion & Mini‑Batch Lifecycle

```mermaid
graph TD
  Raw[Raw Data Arrives<br/>POS Sales, Weather, etc.]
  
  DB[DataBatch<br/>id: batch_001<br/>arrived_at: 2025-05-03 06:00]
  
  DS1[DataSlice<br/>Peak, May 3, Breakfast<br/>covers: 340]
  DS2[DataSlice<br/>Aqueous, May 3, Dinner<br/>covers: 180]
  DS3[DataSlice<br/>Weather, May 3<br/>rain: 100%]
  
  MD1[MetricDefinition<br/>Total Covers]
  MD2[MetricDefinition<br/>Weather Score]
  
  MS1[MetricSeries<br/>Covers for Peak+Breakfast]
  MS2[MetricSeries<br/>Weather Score Daily]
  
  MO1[MetricObservation<br/>May 3: 340 covers]
  MO2[MetricObservation<br/>May 3: 0.0 score]
  
  MO1prev[Previous Observation<br/>May 2: 320 covers]
  
  Raw --> DB
  DB -->|CREATED| DS1
  DB -->|CREATED| DS2  
  DB -->|CREATED| DS3
  
  DS1 -->|FEEDS| MO1
  DS3 -->|FEEDS| MO2
  
  MD1 -->|HAS_SERIES| MS1
  MD2 -->|HAS_SERIES| MS2
  
  MS1 -->|HAS_OBSERVATION| MO1
  MS2 -->|HAS_OBSERVATION| MO2
  
  MO1prev -->|NEXT| MO1
```

1. Create `DataBatch`.
2. Normalize rows → `DataSlice` nodes (`MERGE` to avoid duplication by (dims,time_range)).
3. For each basic `MetricDefinition`: aggregate relevant slices → create new `MetricObservation`s.
4. Link `:NEXT` from prior head(s).
5. Mark changed base metrics; enqueue composite recomputation set.
6. Run composite engine; then anomaly / correlation detectors.
7. Emit `Insight` nodes for material changes.

Error / Late Data Handling:
- Insert replacement observation → link old `:SUPERSEDED_BY` new.
- Trigger recompute only for affected windows (bounded by observation time_start).

---

## 7. Lineage & Explainability Paths

```mermaid
graph LR
  DS1[DataSlice<br/>Peak Covers: 340]
  DS2[DataSlice<br/>Peak Revenue: $5000]
  
  MO1[MetricObservation<br/>Peak Covers<br/>May 3: 340]
  MO2[MetricObservation<br/>Peak Revenue<br/>May 3: $5000]
  
  CompObs[MetricObservation<br/>Revenue Per Cover<br/>May 3: $14.71]
  
  Insight[Insight<br/>RevPerCover dropped<br/>below target $15]
  
  DS1 -->|FEEDS| MO1
  DS2 -->|FEEDS| MO2
  
  CompObs -->|DERIVED_FROM| MO1
  CompObs -->|DERIVED_FROM| MO2
  
  CompObs -->|GENERATES_INSIGHT| Insight
  
  subgraph "Backward Trace (WHY?)"
    CompObs -.->|trace back| MO1
    CompObs -.->|trace back| MO2
    MO1 -.->|trace back| DS1
    MO2 -.->|trace back| DS2
  end
  
  subgraph "Forward Impact (WHAT DEPENDS?)"
    MO1 -.->|impacts| CompObs
    MO2 -.->|impacts| CompObs  
    CompObs -.->|triggers| Insight
  end
```

Backward (WHY?): Observation → `DERIVED_FROM` → source observations → `FEEDS` → raw DataSlices.
Forward (IMPACT?): Observation ← `DERIVED_FROM`* ← composite observations ← Insights.

Minimal explanation query sketch:
```cypher
// Upstream factors for a composite observation
MATCH (co:MetricObservation {id:$id})-[:DERIVED_FROM]->(src:MetricObservation)
OPTIONAL MATCH (src)<-[:FEEDS]-(ds:DataSlice)
RETURN co, collect(distinct src) as inputs, collect(distinct ds) as raw_sources;
```

---

## 8. Retrieval Pattern for LLM / Agent

```mermaid
flowchart TD
  Query[User: Why did staff efficiency drop?]
  
  Step1[1. Resolve MetricDefinition<br/>name embedding/alias match<br/>Staff Efficiency]
  
  Step2[2. Find MetricSeries<br/>dimension signature<br/>restaurant + meal + date range]
  
  Step3[3. Pull recent observations<br/>follow NEXT chain<br/>exclude SUPERSEDED_BY]
  
  Step4[4. Traverse DERIVED_FROM<br/>one hop for decomposition<br/>covers/staff_hours inputs]
  
  Step5[5. Fetch Insights/Anomalies<br/>ABOUT_METRIC_SERIES<br/>ON_OBSERVATION]
  
  Step6[6. Return structured JSON<br/>values, deltas, inputs, anomalies<br/>for LLM summarization]
  
  Response[Agent: Staff efficiency dropped 15%<br/>because covers decreased 20%<br/>while staff hours only reduced 8%]
  
  Query --> Step1
  Step1 --> Step2
  Step2 --> Step3
  Step3 --> Step4
  Step4 --> Step5
  Step5 --> Step6
  Step6 --> Response
```

Steps when a user asks: *"Why did staff efficiency drop?"*
1. Resolve target `MetricDefinition` by name embedding / alias.
2. Fetch `MetricSeries` for dimension signature (restaurant, meal, date range).
3. Pull recent observation chain via `:NEXT` (limit N) excluding superseded.
4. Traverse `:DERIVED_FROM` one hop for decomposition.
5. Fetch any recent `Insight` / `Anomaly` via `:ABOUT_METRIC_SERIES` / `:ON_OBSERVATION`.
6. Return structured JSON (values, deltas, inputs, anomalies) for natural language summarization.

---

## 9. Mermaid Schema (Condensed End‑to‑End)
```mermaid
graph TD
  DB[DataBatch] --> DS[DataSlice]
  DS -->|FEEDS| BO[Basic Obs]
  MD[MetricDef] -->|HAS_SERIES| MS[MetricSeries]
  MS -->|HAS_OBSERVATION| BO
  BO -->|NEXT| B1[Basic Obs+1]
  CMD[CompositeDef] -->|USES_METRIC| MD
  CMD -->|DEFINES_SERIES| CMS[CompositeSeries]
  CMS --> CObs[Composite Obs]
  CObs -->|DERIVED_FROM| BO
    CObs -->|GENERATES_INSIGHT| IN[Insight]
  BO -->|ROLLS_UP_INTO| DDay[Day Agg]
  DDay -->|ROLLS_UP_INTO| WWeek[Week Agg]
```

---

## 10. Advantages vs Prior Version
| Concern | Old Design | Refined Design |
|---------|------------|----------------|
| Multi-dimensional facts | Forced into generic Entity+MetricVersion | Explicit DataSlice with dims map |
| Temporal chaining | Implicit by dates | Explicit `:NEXT`, rollups, revisions |
| Composite clarity | Edge formulas on Metrics | Dedicated CompositeMetricDefinition + expression_dsl |
| Selective recompute | Hard to scope | Reverse dependency traversal via `:USES_METRIC` |
| Explainability | Limited | `DERIVED_FROM` + `FEEDS` + provenance |
| Late data | Overwrite or duplicate | `:SUPERSEDED_BY` chain |
| Agent retrieval | Ad hoc | Structured retrieval pipeline |

---

## 11. Implementation Phasing (Actionable)

```mermaid
flowchart TD
  P1[Phase 1: Foundation<br/>MetricDefinition/Series/Observation<br/>NEXT temporal chaining<br/>Basic ingestion pipeline]
  
  P2[Phase 2: Composites<br/>CompositeMetricDefinition<br/>USES_METRIC dependency graph<br/>Selective recompute engine]
  
  P3[Phase 3: Advanced Features<br/>ROLLS_UP_INTO hierarchies<br/>Anomaly/Insight detection<br/>SUPERSEDED_BY corrections]
  
  P4[Phase 4: Optimization<br/>Correlation analysis<br/>Forecasting capabilities<br/>Observation pruning/archival]
  
  M1[Milestone 1<br/>Can ingest & query basic metrics]
  M2[Milestone 2<br/>Can compute derived metrics]
  M3[Milestone 3<br/>Can handle corrections & insights]
  M4[Milestone 4<br/>Production-ready performance]
  
  P1 --> M1
  M1 --> P2
  P2 --> M2
  M2 --> P3
  P3 --> M3
  M3 --> P4
  P4 --> M4
```

Phase 1: Definitions, Series, Observations, NEXT chain, ingestion pipeline.
Phase 2: CompositeMetricDefinition engine + dependency graph + selective recompute.
Phase 3: Rollups (`:ROLLS_UP_INTO`), anomalies, insights, supersession.
Phase 4: Correlations, forecasting, optimization (caching & pruning old fine-grain observations).

---

## 12. Trade‑Offs & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Observation explosion | Storage & traversal cost | TTL + rollup retention + compress superseded |
| Cyclic composite defs | Infinite recompute | Cycle detection on `:USES_METRIC` commit |
| High fan-out dependency updates | Compute lag | Batch recompute queue + window scoping |
| Late-arriving corrections | Inconsistent views | Revision chain + recompute delta windows |
| Agent over-fetch | Prompt noise | Curated retrieval (recent N + anomalies + dependency cone) |

---


## 13. Concrete Example: Nemacolin Resort Analysis

### Real Data Context
Based on Nemacolin Resort's F&B operations data (May 2-8, 2025), here's how the system works:

#### A. Raw Data & Processed Facts
```mermaid
graph TD
    DB[DataBatch<br/>May 3 POS Import<br/>arrived_at: 06:00]
    
    DS1[DataSlice<br/>restaurant: Peak<br/>date: 2025-05-03, meal: breakfast<br/>covers: 340]
    DS2[DataSlice<br/>restaurant: Aqueous<br/>date: 2025-05-03, meal: dinner<br/>covers: 180] 
    DS3[DataSlice<br/>source: weather_api<br/>date: 2025-05-03<br/>rain_prob: 100%]
    DS4[DataSlice<br/>event: Kentucky_Derby<br/>venue: Peak, date: 2025-05-03<br/>attendance: 450]
    
    DB -->|CREATED| DS1
    DB -->|CREATED| DS2
    DB -->|CREATED| DS3
    DB -->|CREATED| DS4
```

#### B. Metric Definitions, Series & Observations
```mermaid
graph LR
    MD1[MetricDefinition<br/>Total Covers<br/>unit: guest_count<br/>type: basic]
    MD2[MetricDefinition<br/>Revenue Per Cover<br/>unit: dollars<br/>type: basic]
    MD3[MetricDefinition<br/>Staff Efficiency<br/>unit: covers_per_staff<br/>type: basic]
    
    MS1[MetricSeries<br/>Covers for Peak+Breakfast<br/>dims: restaurant=Peak, meal=breakfast]
    MS2[MetricSeries<br/>RevPerCover for Peak+Breakfast<br/>dims: restaurant=Peak, meal=breakfast]
    MS3[MetricSeries<br/>StaffEff for Peak+Breakfast<br/>dims: restaurant=Peak, meal=breakfast]
    
    MO1[MetricObservation<br/>2025-05-03: 340 covers<br/>confidence: 0.85]
    MO2[MetricObservation<br/>2025-05-03: $16.22<br/>confidence: 0.92]
    MO3[MetricObservation<br/>2025-05-03: 56.7<br/>confidence: 0.88]
    
    MD1 -->|HAS_SERIES| MS1
    MD2 -->|HAS_SERIES| MS2
    MD3 -->|HAS_SERIES| MS3
    
    MS1 -->|HAS_OBSERVATION| MO1
    MS2 -->|HAS_OBSERVATION| MO2
    MS3 -->|HAS_OBSERVATION| MO3
    
    DS1 -->|FEEDS| MO1
```

#### C. Composite Metrics Dependencies
```mermaid
graph TD
    MD_Covers[MetricDefinition<br/>Total Covers]
    MD_Revenue[MetricDefinition<br/>Total Revenue]
    MD_Staff[MetricDefinition<br/>Total Staff Hours]
    
    CMD_RevPerCover[CompositeMetricDefinition<br/>Revenue Per Cover<br/>formula: revenue / covers]
    CMD_StaffEff[CompositeMetricDefinition<br/>Staff Efficiency<br/>formula: covers / staff_count]
    CMD_RevPerHour[CompositeMetricDefinition<br/>Revenue Per Staff Hour<br/>formula: revenue / staff_hours]
    
    CMD_RevPerCover -->|USES_METRIC| MD_Covers
    CMD_RevPerCover -->|USES_METRIC| MD_Revenue
    
    CMD_StaffEff -->|USES_METRIC| MD_Covers
    CMD_StaffEff -->|USES_METRIC| MD_Staff
    
    CMD_RevPerHour -->|USES_METRIC| MD_Revenue
    CMD_RevPerHour -->|USES_METRIC| MD_Staff
    
    MS_CompRevPerCover[MetricSeries<br/>RevPerCover for Peak]
    MO_CompRevPerCover[MetricObservation<br/>May 3: $14.71]
    
    CMD_RevPerCover -->|DEFINES_SERIES| MS_CompRevPerCover
    MS_CompRevPerCover -->|HAS_OBSERVATION| MO_CompRevPerCover
```

#### D. Insight Generation from Observations
```mermaid
graph LR
    MO_Sat[MetricObservation<br/>Saturday Covers<br/>May 3: 340]
    MO_Mon[MetricObservation<br/>Monday Covers<br/>May 5: 170]
    
    MO_Weather[MetricObservation<br/>Weather Score<br/>May 2-8: 0.0 avg]
    
    Insight1[Insight<br/>Weekend vs Weekday Pattern<br/>title: 50% drop Mon vs Sat<br/>severity: normal]
    
    Insight2[Insight<br/>Weather Impact Analysis<br/>title: Rain correlation detected<br/>severity: medium]
    
    Anomaly1[Anomaly<br/>Covers Drop<br/>zscore: -2.1<br/>expected: 200, actual: 170]
    
    MO_Sat -->|GENERATES_INSIGHT| Insight1
    MO_Mon -->|GENERATES_INSIGHT| Insight1
    MO_Weather -->|GENERATES_INSIGHT| Insight2
    
    MO_Mon -->|ON_OBSERVATION| Anomaly1
    
    MS_Covers[MetricSeries<br/>Peak Covers]
    Insight1 -->|ABOUT_METRIC_SERIES| MS_Covers
```

#### E. Data Lineage & Processing Flow
```mermaid
graph LR
    DB_POS[DataBatch<br/>POS Sales Import<br/>May 3, 06:00]
    DB_Staff[DataBatch<br/>Staffing Data<br/>May 3, 06:15]
    DB_Weather[DataBatch<br/>Weather API<br/>May 3, 07:00]
    
    DS_Covers[DataSlice<br/>Peak Breakfast Covers: 340]
    DS_Staff[DataSlice<br/>Peak Servers: 3]
    DS_Weather[DataSlice<br/>Rain Probability: 100%]
    
    MO_Covers[MetricObservation<br/>Total Covers: 340]
    MO_Staff[MetricObservation<br/>Server Count: 3]
    
    MO_Efficiency[MetricObservation<br/>Staff Efficiency: 113.3<br/>covers per server]
    
    Insight_Final[Insight<br/>Optimal staffing achieved<br/>efficiency within target range]
    
    DB_POS -->|CREATED| DS_Covers
    DB_Staff -->|CREATED| DS_Staff
    DB_Weather -->|CREATED| DS_Weather
    
    DS_Covers -->|FEEDS| MO_Covers
    DS_Staff -->|FEEDS| MO_Staff
    
    MO_Efficiency -->|DERIVED_FROM| MO_Covers
    MO_Efficiency -->|DERIVED_FROM| MO_Staff
    
    MO_Efficiency -->|GENERATES_INSIGHT| Insight_Final
```

### Real Business Questions the System Can Answer

#### 1. **Staffing Optimization Query**
> *"Why did The Peak need 3 servers on Saturday but only 1 on Monday?"*

**Graph Traversal:**
```cypher
// Find covers and server observations for Peak restaurant in date range
MATCH (md_covers:MetricDefinition {name:"Total_Covers"})-[:HAS_SERIES]->(ms_covers:MetricSeries)
WHERE ms_covers.dims_signature CONTAINS "restaurant=Peak"
MATCH (ms_covers)-[:HAS_OBSERVATION]->(covers_obs:MetricObservation)
WHERE covers_obs.time_start >= date("2025-05-03") AND covers_obs.time_start <= date("2025-05-05")

MATCH (md_servers:MetricDefinition {name:"Server_Count"})-[:HAS_SERIES]->(ms_servers:MetricSeries)
WHERE ms_servers.dims_signature CONTAINS "restaurant=Peak"
MATCH (ms_servers)-[:HAS_OBSERVATION]->(server_obs:MetricObservation)
WHERE server_obs.time_start = covers_obs.time_start

RETURN covers_obs.time_start as date, 
       covers_obs.value as covers, 
       server_obs.value as servers, 
       (covers_obs.value/server_obs.value) as covers_per_server
```

**System Response:** *"Saturday had 340 covers requiring 3 servers (113 covers/server), while Monday had 170 covers with 1 server (170 covers/server). The efficiency ratio suggests Monday was understaffed by 1 server for optimal service."*

#### 2. **Weather Impact Analysis**
> *"How did the 7-day rain streak affect our outdoor dining venues?"*

**Graph Traversal:**
```cypher
// Find weather observations and correlate with outdoor covers
MATCH (weather_md:MetricDefinition {name:"Weather_Score"})-[:HAS_SERIES]->(weather_ms:MetricSeries)
MATCH (weather_ms)-[:HAS_OBSERVATION]->(weather_obs:MetricObservation)
WHERE weather_obs.time_start >= date("2025-05-02") AND weather_obs.time_start <= date("2025-05-08")

MATCH (covers_md:MetricDefinition {name:"Outdoor_Covers"})-[:HAS_SERIES]->(covers_ms:MetricSeries)
MATCH (covers_ms)-[:HAS_OBSERVATION]->(covers_obs:MetricObservation)
WHERE covers_obs.time_start = weather_obs.time_start

OPTIONAL MATCH (covers_obs)-[:GENERATES_INSIGHT]->(insight:Insight)

RETURN covers_ms.dims_signature as venue, 
       covers_obs.value as outdoor_covers, 
       weather_obs.value as weather_score,
       insight.title as weather_insight
```

#### 3. **Revenue Anomaly Detection**
> *"The Peak's revenue dropped to $0 all week - what happened?"*

**System Analysis:**
```mermaid
graph TD
    Revenue_Obs[MetricObservation<br/>Peak Revenue: $0<br/>May 2-8, 2025]
    Covers_Obs[MetricObservation<br/>Peak Covers: 340<br/>Saturday May 3]
    
    Revenue_Anomaly[Anomaly<br/>Zero Revenue Alert<br/>zscore: -5.2<br/>expected: $5000, actual: $0]
    
    Insight_Anomaly[Insight<br/>Revenue-Covers Mismatch<br/>severity: critical<br/>Revenue system may be down]
    
    Revenue_Obs -->|ON_OBSERVATION| Revenue_Anomaly
    Revenue_Obs -->|GENERATES_INSIGHT| Insight_Anomaly
    Covers_Obs -->|GENERATES_INSIGHT| Insight_Anomaly
    
    RevPerCover_Obs[MetricObservation<br/>RevPerCover: $0<br/>DERIVED_FROM revenue + covers]
    
    RevPerCover_Obs -->|DERIVED_FROM| Revenue_Obs
    RevPerCover_Obs -->|DERIVED_FROM| Covers_Obs
```

### LLM Agent Decision Flow

#### Agent Query Processing:
1. **Parse Question:** "Should we increase staffing for next weekend?"
2. **Graph Search:** Find historical weekend patterns + weather forecast + event calendar
3. **Metric Analysis:** Compare covers/staff ratios, revenue/cover trends
4. **Insight Generation:** Trigger predictive analytics task if needed
5. **Recommendation:** "Based on Kentucky Derby event + clear weather forecast, increase servers from 3 to 4 for Saturday"

#### Automated Task Triggering:
```mermaid
graph TD
    NewData[New POS Data Arrives]
    MetricCalc[Calculate: Revenue Per Cover]
    Threshold{Revenue < $15/cover?}
    
    NewData --> MetricCalc
    MetricCalc --> Threshold
    Threshold -->|Yes| TriggerAlert[Trigger: Low Performance Alert]
    Threshold -->|No| Continue[Continue Normal Processing]
    
    TriggerAlert --> TaskML[Task: Analyze Cause<br/>- Menu analysis<br/>- Service time analysis<br/>- Competition check]
```
