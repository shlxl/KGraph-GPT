import pytest
import os
# Add the project root to the path to allow importing 'app'
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import generate_graph, KnowledgeGraph, Node, Relationship

# --- Integration Test ---

# Note: This is an integration test that makes a real API call.
# In a larger project, you would mock the LLM call to create a pure unit test.

SAMPLE_TEXT = "爱因斯坦出生于德国，后来移居美国。"

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY is not set")
def test_graph_generation_and_content():
    """Tests if the graph generation function runs and extracts expected entities."""
    # 1. Generate the graph from the sample text
    graph = generate_graph(SAMPLE_TEXT, source="test", model_name="gemini-2.5-pro", node_color="#FFADAD", edge_color="#9BF6FF", rel_set_name="GraphRAG-RELSET-GenericWeb-zh")

    # 2. Assert that the graph and its components are not empty
    assert graph is not None
    assert isinstance(graph, KnowledgeGraph)
    assert len(graph.nodes) > 0
    assert len(graph.relationships) > 0
    assert graph.metadata is not None
    assert graph.metadata.source == "test"

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


# --- Unit Test ---

def test_generate_graph_with_mock_llm(mocker):
    """Tests the graph generation function with a mocked LLM and dynamic prompt."""
    # Mock REL_SETS and PROMPT_TEMPLATE
    mock_rel_sets = {
        "test_rel_set": {
            "relations": [{"name": "test_relation_1"}, {"name": "test_relation_2"}],
            "qualifiers": {"test_qualifier": "string"},
            "policies": {"evidence_min_unit": "sentence"},
            "authority_order_for_disputes": ["GovernmentAgency"]
        }
    }
    mocker.patch('app.REL_SETS', mock_rel_sets)
    mocker.patch('app.PROMPT_TEMPLATE', "SYSTEM_PROMPT_TEMPLATE {REL_SET} {QUALIFIERS}\n抽取策略与证据规则：\n{{POLICIES}}\n\n权威来源排序（用于争议解决）：\n{{AUTHORITY_ORDER}}")

    # 1. Create a fake KnowledgeGraph object to be returned by the mock
    node_a = Node(id="Node A", type="Person")
    node_b = Node(id="Node B", type="Place")
    # The mock chain will return a graph without metadata
    fake_graph_from_llm = KnowledgeGraph(
        nodes=[node_a, node_b],
        relationships=[Relationship(source=node_a, target=node_b, type="Located In")]
    )

    # 2. Setup the mock for the entire chain
    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = fake_graph_from_llm

    # 3. Mock the LLM and the `with_structured_output` call
    mock_llm = mocker.MagicMock()
    mock_structured_llm = mocker.MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    get_llm_mock = mocker.patch('app.get_llm', return_value=mock_llm)

    # 4. Mock the prompt template and the pipe (`|`) operation
    mock_chat_prompt_template = mocker.patch('app.ChatPromptTemplate.from_messages')
    mock_prompt_instance = mocker.MagicMock()
    mock_prompt_instance.__or__.return_value = mock_chain
    mock_chat_prompt_template.return_value = mock_prompt_instance

    # 5. Call the function under test
    result_graph = generate_graph("some dummy text", source="test_source", model_name="gemini-2.5-pro", node_color="#FFADAD", edge_color="#9BF6FF", rel_set_name="test_rel_set")

    # 6. Assert the result
    # Check that the nodes and relationships are what we expect
    assert result_graph.nodes == fake_graph_from_llm.nodes
    assert result_graph.relationships == fake_graph_from_llm.relationships
    # Check that metadata was added correctly
    assert result_graph.metadata is not None
    assert result_graph.metadata.source == "test_source"
    assert isinstance(result_graph.metadata.timestamp, str)
    # Check that colors were added correctly
    assert result_graph.nodes[0].color == "#FFADAD"
    assert result_graph.relationships[0].color == "#9BF6FF"

    # 7. Verify that the mocks were called as expected
    get_llm_mock.assert_called_once_with("gemini-2.5-pro")
    mock_llm.with_structured_output.assert_called_once_with(KnowledgeGraph)
    
    expected_relations_str = '"test_relation_1",\n  "test_relation_2"'
    expected_qualifiers_str = '{\n  "test_qualifier": "string"\n}'
    expected_policies_str = '{{\n  "evidence_min_unit": "sentence"\n}}'
    expected_authority_order_str = '[\n  "GovernmentAgency"\n]'

    expected_system_prompt = f"SYSTEM_PROMPT_TEMPLATE {expected_relations_str} {expected_qualifiers_str}\n抽取策略与证据规则：\n{expected_policies_str}\n\n权威来源排序（用于争议解决）：\n{expected_authority_order_str}"

    mock_chat_prompt_template.assert_called_once_with([
        ("system", expected_system_prompt),
        ("human", "请从以下文本中提取知识图谱：\n\n{text}")
    ])
    mock_prompt_instance.__or__.assert_called_once_with(mock_structured_llm)
    mock_chain.invoke.assert_called_once_with({"text": "some dummy text"})