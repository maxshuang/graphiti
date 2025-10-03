#!/usr/bin/env python3
"""Test the fixed community building with debug output."""

import asyncio
import logging
import sys
from graphiti_core import Graphiti

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    client = Graphiti(
        'bolt://localhost:7687',
        'neo4j', 
        'password'
    )
    group_id = "podcast-example"
    
    print("🏘️ Testing improved community building...")
    try:
        communities, community_edges = await client.build_communities(group_ids=[group_id])
        print(f"✅ Successfully created {len(communities)} communities with {len(community_edges)} edges")
        
        for i, community in enumerate(communities):
            print(f"  Community {i+1}: {community.name}")
            
    except Exception as e:
        print(f"❌ Error during community building: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())