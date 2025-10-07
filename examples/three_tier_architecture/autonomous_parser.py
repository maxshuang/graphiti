#!/usr/bin/env python3
"""
Autonomous Three-Tier Architecture Parser

This script demonstrates how to leverage Graphiti's autonomous LLM-driven 
entity extraction with ALL the custom node and edge types defined in custom_types.py.

Usage:
    python autonomous_parser.py
"""

import asyncio
import logging
import os
import sys

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from custom_types import (
    # Import ALL the custom types we defined
    DataBatch, DataSlice, MetricDefinition, MetricSeries, MetricObservation, 
    CompositeMetricDefinition, Insight, Anomaly, Correlation,
    CreatedEdge, FeedsEdge, HasSeriesEdge, HasObservationEdge, 
    GeneratesInsightEdge, UsesMetricEdge, DerivedFromEdge, CorrelatesWithEdge
)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Constants
GROUP_ID = "autonomous-analysis"
REPORT_PATH = "/Users/maxhuang/projects/llm/graphiti/examples/data/analysis_report.md"


class AutonomousThreeTierParser:
    """
    Parser that uses ALL custom node/edge types while letting Graphiti's LLM 
    autonomously identify entities and relationships.
    """
    
    def __init__(self):
        neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')  
        neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
        
        self.client = Graphiti(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )
        
        # Use ALL the custom entity types we defined
        self.entity_types = {
            # Cold Tier - Raw Data
            'DataBatch': DataBatch,
            'DataSlice': DataSlice,
            
            # Warm Tier - Structured Metrics  
            'MetricDefinition': MetricDefinition,
            'MetricSeries': MetricSeries,
            'MetricObservation': MetricObservation,
            'CompositeMetricDefinition': CompositeMetricDefinition,
            
            # Hot Tier - Intelligence
            'Insight': Insight,
            'Anomaly': Anomaly,
            'Correlation': Correlation
        }
        
        # Use ALL the custom edge types we defined
        self.edge_types = {
            'CREATED': CreatedEdge,
            'FEEDS': FeedsEdge,
            'HAS_SERIES': HasSeriesEdge,
            'HAS_OBSERVATION': HasObservationEdge,
            'GENERATES_INSIGHT': GeneratesInsightEdge,
            'USES_METRIC': UsesMetricEdge,
            'DERIVED_FROM': DerivedFromEdge,
            'CORRELATES_WITH': CorrelatesWithEdge
        }
        
        # Define ALL the relationships between our custom types
        self.edge_type_map = {
            # Cold Tier Relationships
            ('DataBatch', 'DataSlice'): ['CREATED'],
            
            # Cold → Warm Relationships
            ('DataSlice', 'MetricObservation'): ['FEEDS'],
            ('DataBatch', 'MetricDefinition'): ['CREATED'],
            
            # Warm Tier Internal Relationships
            ('MetricDefinition', 'MetricSeries'): ['HAS_SERIES'],
            ('MetricSeries', 'MetricObservation'): ['HAS_OBSERVATION'],
            ('CompositeMetricDefinition', 'MetricDefinition'): ['USES_METRIC'],
            ('MetricObservation', 'MetricObservation'): ['DERIVED_FROM'],
            
            # Warm → Hot Relationships
            ('MetricObservation', 'Insight'): ['GENERATES_INSIGHT'],
            ('MetricObservation', 'Anomaly'): ['GENERATES_INSIGHT'],
            ('MetricObservation', 'Correlation'): ['CORRELATES_WITH'],
            
            # Hot Tier Internal Relationships
            ('Insight', 'Anomaly'): ['CORRELATES_WITH'],
            ('Correlation', 'Insight'): ['GENERATES_INSIGHT']
        }
    
    async def parse_report_autonomously(self):
        """
        Parse report with ALL custom types, letting Graphiti's LLM identify 
        which entities fit which custom types.
        """
        
        logger.info("🧠 Starting autonomous parsing with ALL custom node/edge types...")
        logger.info(f"📁 Reading report from: {REPORT_PATH}")
        
        # Check if file exists
        if not os.path.exists(REPORT_PATH):
            raise FileNotFoundError(f"Report file not found: {REPORT_PATH}")
        
        # Read the raw report content
        with open(REPORT_PATH, 'r') as f:
            report_content = f.read()
            
        logger.info(f"📄 Report content length: {len(report_content)} characters")
        
        # Let Graphiti's LLM extract entities using ALL our custom types
        await self.client.add_episode(
            name="Business Analysis Report",
            episode_body=report_content,
            source=EpisodeType.text,
            source_description="Restaurant operational analysis with full custom type schema",
            group_id=GROUP_ID,
            entity_types=self.entity_types,  # ALL custom entity types
            edge_types=self.edge_types,      # ALL custom edge types  
            edge_type_map=self.edge_type_map, # ALL relationships
            update_communities=True
        )
        
        logger.info("✅ Autonomous extraction with ALL custom types complete!")
        
        # Analyze what the LLM discovered for each custom type
        await self._analyze_all_discovered_types()
    
    async def _analyze_all_discovered_types(self):
        """Analyze what the LLM discovered for each of our custom entity types."""
        
        logger.info("🔍 Analyzing LLM discoveries for ALL custom types...")
        
        # Check each custom type to see what the LLM discovered
        type_discoveries = {}
        
        for type_name in self.entity_types.keys():
            search_results = await self.client.search(
                query=f"{type_name} {type_name.lower()}",
                group_ids=[GROUP_ID]
            )
            type_discoveries[type_name] = search_results.nodes
            logger.info(f"📊 {type_name}: {len(search_results.nodes)} entities discovered")
        
        # Show examples for each type
        for type_name, nodes in type_discoveries.items():
            if nodes:
                logger.info(f"   └─ Example {type_name}: {nodes[0].name}")
        
        return type_discoveries
    
    async def demo_full_architecture_queries(self):
        """
        Demonstrate queries across all three tiers using all custom types.
        """
        
        logger.info("⚡ Demonstrating queries across ALL custom types...")
        
        # Cold Tier: DataBatch, DataSlice
        cold_results = await self.client.search(
            query="DataBatch DataSlice raw ingestion source data",
            group_ids=[GROUP_ID]
        )
        logger.info(f"❄️ Cold Tier: {len(cold_results.nodes)} raw data entities")
        
        # Warm Tier: MetricDefinition, MetricSeries, MetricObservation, CompositeMetricDefinition
        warm_results = await self.client.search(
            query="MetricDefinition MetricSeries MetricObservation CompositeMetricDefinition",
            group_ids=[GROUP_ID]
        )
        logger.info(f"🔥 Warm Tier: {len(warm_results.nodes)} metric entities")
        
        # Hot Tier: Insight, Anomaly, Correlation
        hot_results = await self.client.search(
            query="Insight Anomaly Correlation pattern trend",
            group_ids=[GROUP_ID]
        )
        logger.info(f"🔥 Hot Tier: {len(hot_results.nodes)} intelligence entities")
        
        # Check relationships between tiers
        await self._check_tier_relationships()
    
    async def _check_tier_relationships(self):
        """Check if the LLM created relationships between our custom types."""
        
        logger.info("� Checking relationships between custom types...")
        
        # Search for each edge type we defined
        for edge_type in self.edge_types.keys():
            edge_results = await self.client.search(
                query=f"{edge_type} relationship connection",
                group_ids=[GROUP_ID]
            )
            logger.info(f"   🔗 {edge_type}: {len(edge_results.edges)} relationships found")


async def main():
    """Run the autonomous parsing with ALL custom types."""
    
    parser = AutonomousThreeTierParser()
    
    try:
        # Parse report autonomously with ALL custom types
        await parser.parse_report_autonomously()
        
        # Demonstrate queries across ALL tiers and types
        await parser.demo_full_architecture_queries()
        
        logger.info("🎉 Full autonomous architecture with ALL custom types complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during autonomous parsing: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())