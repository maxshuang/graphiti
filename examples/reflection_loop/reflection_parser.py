#!/usr/bin/env python3
"""
Reflection Loop Parser for Analysis Report

Implements the simplified design with continuous insight discovery:
1. Parse analysis_report.md into core entities (DataSource, MetricDefinition, MetricObservation, Insight)
2. Run reflection loop to discover patterns and generate meta-insights
3. Self-grow the graph through semantic reasoning

This demonstrates the "semantic reasoning cache" approach where insights
build upon each other through continuous reflection.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import uuid

# Add project root to Python path so we can import graphiti_core
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Graphiti imports - Updated based on other examples
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from dotenv import load_dotenv

# Custom types
from custom_types import (
    ENTITY_TYPES, EDGE_TYPES, EDGE_TYPE_MAP,
    DataSource, MetricDefinition, MetricObservation, Insight, TimePeriod,
    MetaInsight, InsightCluster,
    create_observation_id, create_period_label
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReflectionLoopParser:
    """
    Simplified parser that builds understanding through reflection loops.
    
    The key innovation: instead of predefined schemas, we let insights
    build upon each other to create emergent understanding.
    """
    
    def __init__(self):
        # Load environment variables like other examples
        load_dotenv()
        
        # Neo4j connection setup (following ecommerce/podcast pattern)
        self.neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        self.neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
        self.neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
        
        # Use specific group_id like other examples for data isolation
        self.group_id = 'reflection-loop-example'
        
        self.graphiti = None
        self.reflection_cycles = 0
        
    async def initialize(self):
        """Initialize Graphiti with custom types (following podcast/ecommerce pattern)"""
        logger.info("🚀 Initializing Reflection Loop Parser...")
        
        # Initialize Graphiti like other examples
        self.graphiti = Graphiti(
            uri=self.neo4j_uri,
            user=self.neo4j_user, 
            password=self.neo4j_password
        )
        
        # Clear data for our specific group_id (not entire database)
        logger.info(f"🧹 Clearing data for group_id: {self.group_id}")
        await clear_data(self.graphiti.driver, group_ids=[self.group_id])
        
        # Build indices and constraints like other examples
        await self.graphiti.build_indices_and_constraints()
        logger.info("✅ Graphiti initialized with reflection loop types")
        
    async def parse_analysis_report(self, report_path: str) -> Dict[str, Any]:
        """
        Parse analysis report and extract core entities autonomously.
        
        This is the initial seeding - we let the LLM identify:
        - What data sources are mentioned
        - What metrics are being analyzed  
        - What observations are reported
        - What insights are drawn
        """
        logger.info(f"📖 Parsing analysis report: {report_path}")
        
        # Read the report
        report_content = Path(report_path).read_text()
        
        # Create analysis episode
        episode_content = f"""
        {report_content}     
        """
        
        # Add to graphiti for entity extraction (following autonomous_parser pattern)
        result = await self.graphiti.add_episode(
            name=f"analysis_report_processing_{datetime.now().isoformat()}",
            episode_body=episode_content,
            source=EpisodeType.text,  # Added source type like other examples
            source_description="Analysis report autonomous parsing",
            reference_time=datetime.now(),  # Add required reference_time parameter
            group_id=self.group_id,  # Use our group_id for isolation
            entity_types=ENTITY_TYPES,  # Pass our custom types
            edge_types=EDGE_TYPES,
            edge_type_map=EDGE_TYPE_MAP
        )
        
        logger.info(f"✅ Parsed report into {len(result.nodes)} nodes and {len(result.edges)} edges")
        return {
            'nodes': len(result.nodes),
            'edges': len(result.edges),
            'episode_uuid': result.episode.uuid  # Fixed attribute access
        }
    
    async def run_reflection_cycle(self) -> Dict[str, Any]:
        """
        Run one reflection cycle to discover patterns in insights.
        
        This is where the magic happens:
        1. Query existing insights
        2. Look for patterns, clusters, confirmations
        3. Generate meta-insights about the insights
        4. Self-grow the graph with new understanding
        """
        self.reflection_cycles += 1
        logger.info(f"🔍 Running reflection cycle #{self.reflection_cycles}")
        
        # Search for existing insights to reflect upon (add group_ids filter)
        insights_query = "insights patterns observations conclusions analysis"
        search_results = await self.graphiti.search(
            query=insights_query,
            num_results=20,
            group_ids=[self.group_id]  # Filter to our data only
        )
        
        if not search_results.nodes:
            logger.info("No insights found for reflection - skipping cycle")
            return {'reflected_nodes': 0, 'new_insights': 0}
        
        # Extract insight content for pattern analysis
        insight_content = []
        for node in search_results.nodes:
            if hasattr(node, 'insight_summary'):
                insight_content.append(f"Insight: {node.insight_summary}")
            elif hasattr(node, 'business_impact'):
                insight_content.append(f"Business Impact: {node.business_impact}")
        
        # Create reflection episode
        reflection_episode = f"""
        REFLECTION LOOP ANALYSIS - Cycle {self.reflection_cycles}
        
        Previous Insights Discovered:
        {chr(10).join(insight_content)}
        
        Meta-Analysis Tasks:
        1. Identify SIMILAR_TO relationships between insights
        2. Find insights that CONFIRM each other
        3. Discover InsightCluster patterns - group related insights
        4. Generate MetaInsight - what do these patterns tell us?
        5. Look for contradictions or anomalies
        
        Focus on:
        - What higher-level patterns emerge?
        - What business themes are repeated?
        - What predictive insights can be inferred?
        - How do temporal patterns connect?
        
        Generate new meta-insights about what we're learning about the business.
        """
        
        # Add reflection episode (with proper parameters)
        result = await self.graphiti.add_episode(
            name=f"reflection_cycle_{self.reflection_cycles}_{datetime.now().isoformat()}",
            episode_body=reflection_episode,
            source=EpisodeType.text,
            source_description="Reflection loop pattern discovery",
            reference_time=datetime.now(),  # Add required reference_time parameter
            group_id=self.group_id,
            entity_types=ENTITY_TYPES,  # Keep using our custom types
            edge_types=EDGE_TYPES,
            edge_type_map=EDGE_TYPE_MAP
        )
        
        logger.info(f"🧠 Reflection cycle generated {len(result.nodes)} new nodes, {len(result.edges)} new edges")
        return {
            'reflected_nodes': len(search_results.nodes),
            'new_insights': len(result.nodes),
            'new_edges': len(result.edges),
            'cycle_number': self.reflection_cycles
        }
    
    async def query_understanding(self, question: str) -> Dict[str, Any]:
        """
        Query the built understanding using natural language.
        
        This demonstrates how the reflection loop creates a semantic
        reasoning cache that can answer business questions.
        """
        logger.info(f"❓ Querying understanding: {question}")
        
        search_results = await self.graphiti.search(
            query=question,
            num_results=15,
            group_ids=[self.group_id]  # Filter to our data only
        )
        
        # Analyze what types of entities we found
        entity_types = {}
        relationships = []
        
        for node in search_results.nodes:
            node_type = type(node).__name__
            entity_types[node_type] = entity_types.get(node_type, 0) + 1
        
        for edge in search_results.edges:
            relationships.append(edge.relation_type)
        
        return {
            'question': question,
            'nodes_found': len(search_results.nodes),
            'edges_found': len(search_results.edges),
            'entity_types': entity_types,
            'relationships': list(set(relationships)),
            'search_results': search_results
        }
    
    async def continuous_reflection_loop(self, max_cycles: int = 5) -> List[Dict[str, Any]]:
        """
        Run multiple reflection cycles to build deep understanding.
        
        Each cycle builds on previous cycles, creating increasingly
        sophisticated meta-insights about the business domain.
        """
        logger.info(f"🔄 Starting continuous reflection loop ({max_cycles} cycles)")
        
        results = []
        for cycle in range(max_cycles):
            cycle_result = await self.run_reflection_cycle()
            results.append(cycle_result)
            
            # Break if no new insights generated
            if cycle_result.get('new_insights', 0) == 0:
                logger.info(f"No new insights generated in cycle {cycle + 1} - stopping")
                break
                
            # Small delay between cycles
            await asyncio.sleep(1)
        
        logger.info(f"🏁 Completed {len(results)} reflection cycles")
        return results


async def main():
    """
    Demonstrate the reflection loop approach with analysis_report.md
    """
    print("🧠 Reflection Loop Parser - Simplified Design Demo")
    print("=" * 60)
    
    # Initialize parser
    parser = ReflectionLoopParser()
    await parser.initialize()
    
    # Close client at end like other examples
    try:
        # Parse the analysis report
        report_path = "/Users/maxhuang/projects/llm/graphiti/examples/data/analysis_report.md"
        parse_results = await parser.parse_analysis_report(report_path)
        print(f"\n📊 Initial Parse Results:")
        print(f"   Nodes: {parse_results['nodes']}")
        print(f"   Edges: {parse_results['edges']}")
        
        # TEMPORARILY COMMENTED OUT - Testing just the parsing phase
        # Run reflection loops to build understanding
        # print(f"\n🔄 Running Reflection Loops...")
        # reflection_results = await parser.continuous_reflection_loop(max_cycles=3)
        # 
        # for i, result in enumerate(reflection_results):
        #     print(f"   Cycle {i+1}: {result.get('new_insights', 0)} new insights, {result.get('new_edges', 0)} new edges")
        
        # TEMPORARILY COMMENTED OUT - Testing understanding queries (without reflection loops)
        # print(f"\n❓ Testing Initial Understanding Queries:")
        # 
        # test_questions = [
        #     "What are the main business trends identified?",
        #     "Which metrics show concerning patterns?", 
        #     "What seasonal patterns were discovered?",
        #     "What recommendations were made?",
        #     "How do different business areas relate?"
        # ]
        # 
        # for question in test_questions:
        #     result = await parser.query_understanding(question)
        #     print(f"\nQ: {question}")
        #     print(f"A: Found {result['nodes_found']} relevant nodes, {result['edges_found']} relationships")
        #     print(f"   Entity types: {result['entity_types']}")
        #     if result['relationships']:
        #         print(f"   Relationships: {result['relationships'][:3]}...")  # Show first 3
        
        print(f"\n✅ Initial Parse Demo Complete!")
        print(f"   Focus: Testing entity extraction from analysis report")
        # print(f"   Total reflection cycles: {parser.reflection_cycles}")
        
    finally:
        # Always close the client connection like other examples
        if parser.graphiti:
            await parser.graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())