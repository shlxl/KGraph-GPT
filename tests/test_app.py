import pytest
import os
# Add the project root to the path to allow importing 'app'
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import generate_graph, KnowledgeGraph

# Note: This is an integration test that makes a real API call.
# In a larger project, you would mock the LLM call to create a pure unit test.

SAMPLE_TEXT = "爱因斯坦出生于德国，后来移居美国。"

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY is not set")
def test_graph_generation_and_content():
    """Tests if the graph generation function runs and extracts expected entities."""
    # 1. Generate the graph from the sample text
    graph = generate_graph(SAMPLE_TEXT)

    # 2. Assert that the graph and its components are not empty
    assert graph is not None
    assert isinstance(graph, KnowledgeGraph)
    assert len(graph.nodes) > 0
    assert len(graph.relationships) > 0

    # 3. Check for the existence of key nodes
    # Note: The LLM may normalize names, so we check for variations.
    node_ids = {node.id.lower() for node in graph.nodes}
    assert "albert einstein" in node_ids or "爱因斯坦" in node_ids
    assert "germany" in node_ids or "德国" in node_ids
    assert "united states" in node_ids or "美国" in node_ids

    # 4. Check for the existence of a key relationship
    birthplace_relationship_found = False
    for rel in graph.relationships:
        source_id = rel.source.id.lower()
        target_id = rel.target.id.lower()
        
        # Check for (Einstein -> born in -> Germany)
        if ("einstein" in source_id or "爱因斯坦" in source_id) and \
           ("germany" in target_id or "德国" in target_id):
            birthplace_relationship_found = True
            break
            
    assert birthplace_relationship_found, "Did not find the 'born in' relationship between Einstein and Germany"
