# Reflection Loop Example

This example demonstrates the **simplified design with reflection loop** approach to building a graph-based understanding layer. Instead of complex predefined schemas, it focuses on core semantic concepts that build understanding through continuous reflection.

## Core Philosophy

The reflection loop approach treats the graph as a **semantic reasoning cache** where insights continuously build upon each other:

1. **Initial Seeding**: Parse raw data into core entities (DataSource, MetricDefinition, MetricObservation, Insight)
2. **Reflection Cycles**: Analyze existing insights to discover patterns, clusters, and meta-insights  
3. **Self-Growth**: The graph grows more sophisticated through each reflection cycle
4. **Emergent Understanding**: Complex business understanding emerges from simple building blocks

## Architecture

### Core Node Types
- **DataSource**: Pointers to external data systems (Cold Tier)
- **MetricDefinition**: Semantic contracts for measurable concepts
- **MetricObservation**: Aggregated metric values for time windows (Warm Tier) 
- **Insight**: Interpreted conclusions and patterns (Hot Tier)
- **TimePeriod**: Optional temporal grouping for reasoning

### Reflection Loop Extensions
- **MetaInsight**: Generalized patterns discovered through reflection
- **InsightCluster**: Groups of semantically similar insights

### Key Relationships
- `FEEDS`: DataSource → MetricObservation (data lineage)
- `GENERATES_INSIGHT`: MetricObservation → Insight (analysis results)
- `SIMILAR_TO`: Insight → Insight (discovered by reflection)
- `CONFIRMS`: Insight → Insight (mutual reinforcement)
- `BELONGS_TO`: Insight → InsightCluster (semantic grouping)
- `EVOLVES_INTO`: InsightCluster → MetaInsight (pattern abstraction)

## Files

### `custom_types.py`
Defines the simplified Pydantic schemas for all node and edge types. Key features:
- Domain-agnostic design with flexible dimensions
- Clean separation between core data flow and reflection loop
- Complete type mappings for Graphiti integration

### `reflection_parser.py` 
Main implementation that demonstrates:
- **Autonomous parsing** of `analysis_report.md` into core entities
- **Continuous reflection loops** that discover patterns in existing insights
- **Natural language querying** of the built understanding
- **Self-growing graph** that becomes more sophisticated over time

## Usage

```bash
# Install dependencies (from repo root)
uv sync --extra dev

# Run the reflection loop demo
cd examples/reflection_loop
python reflection_parser.py
```

## What It Does

1. **Parses** the `examples/data/analysis_report.md` file autonomously
2. **Extracts** DataSource, MetricDefinition, MetricObservation, and Insight entities
3. **Runs reflection cycles** to discover patterns between insights
4. **Generates meta-insights** about business trends and relationships
5. **Tests understanding** with natural language queries

## Expected Output

The demo will show:
- Initial parsing results (nodes/edges extracted)
- Multiple reflection cycles building understanding
- Query results demonstrating semantic reasoning capabilities
- Evidence of the graph becoming more sophisticated through reflection

## Key Innovation

Unlike traditional approaches that require complex predefined schemas, this approach:
- Starts simple with core semantic building blocks
- Builds sophistication through reflection rather than complexity
- Creates emergent understanding that wasn't explicitly programmed
- Enables natural language business reasoning from day one

This demonstrates how a "semantic reasoning cache" can provide immediate business value while continuously improving its understanding of the domain.