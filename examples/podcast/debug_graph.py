#!/usr/bin/env python3
"""Check current graph status to understand the community building performance issue."""

import asyncio
from graphiti_core import Graphiti


async def main():
    client = Graphiti(
        'bolt://localhost:7687',
        'neo4j', 
        'password'
    )
    group_id = "podcast-example"

    # Query node and edge counts
    query = """
    MATCH (n)
    WHERE n.group_id = $group_id
    RETURN labels(n)[0] as node_type, count(n) as count
    ORDER BY count DESC
    """
    
    records, _, _ = await client.driver.execute_query(query, group_id=group_id)
    
    print("Node counts by type:")
    for record in records:
        print(f"  {record['node_type']}: {record['count']}")
    
    # Query RELATES_TO edge details
    edge_query = """
    MATCH (a:Entity {group_id: $group_id})-[r:RELATES_TO]-(b:Entity {group_id: $group_id})
    RETURN count(r) as total_relates_to_edges,
           count(DISTINCT a) as nodes_with_relations,
           avg(degree) as avg_degree
    WHERE degree = (
        SELECT count(*)
        FROM (MATCH (a)-[:RELATES_TO]-() RETURN 1)
    )
    """
    
    # Simpler query for edge stats
    simple_edge_query = """
    MATCH (a:Entity {group_id: $group_id})-[r:RELATES_TO]-(b:Entity {group_id: $group_id})
    RETURN count(r) as total_relates_to_edges
    """
    
    edge_records, _, _ = await client.driver.execute_query(simple_edge_query, group_id=group_id)
    
    print(f"\nRELATES_TO edges: {edge_records[0]['total_relates_to_edges']}")
    
    # Check node degrees (how many connections each node has)
    degree_query = """
    MATCH (n:Entity {group_id: $group_id})
    OPTIONAL MATCH (n)-[r:RELATES_TO]-()
    WITH n, count(r) as degree
    RETURN min(degree) as min_degree, max(degree) as max_degree, 
           avg(degree) as avg_degree, count(n) as total_nodes
    """
    
    degree_records, _, _ = await client.driver.execute_query(degree_query, group_id=group_id)
    
    if degree_records:
        dr = degree_records[0]
        print(f"\nNode degree statistics:")
        print(f"  Min degree: {dr['min_degree']}")
        print(f"  Max degree: {dr['max_degree']}")
        print(f"  Average degree: {dr['avg_degree']:.2f}")
        print(f"  Total nodes: {dr['total_nodes']}")

if __name__ == "__main__":
    asyncio.run(main())