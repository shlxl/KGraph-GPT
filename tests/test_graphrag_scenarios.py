import pytest
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any

# Assuming app.py is in the parent directory for imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import generate_graph, normalize_entities, KnowledgeGraph, Node, Relationship, Metadata, REL_SETS, PROMPT_TEMPLATE

# --- Fixtures ---

@pytest.fixture(scope="module")
def coralwind_corpus_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'GraphRAG-Extract-Best-Example-CoralWind-zh', 'corpus'))

@pytest.fixture(scope="module")
def coralwind_gold_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'GraphRAG-Extract-Best-Example-CoralWind-zh', 'gold'))

@pytest.fixture(scope="module")
def mentions_data(coralwind_gold_path) -> List[Dict[str, Any]]:
    mentions_file_path = os.path.join(coralwind_gold_path, "mentions.jsonl")
    data = []
    with open(mentions_file_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

@pytest.fixture(scope="module")
def d1_news_content(coralwind_corpus_path) -> str:
    file_path = os.path.join(coralwind_corpus_path, "d1_news_2025-03-12.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d2_brief_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d2_brief_2025-05-01.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d3_permit_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d3_permit_2025-06-10.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d4_rumor_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d4_rumor_2025-06-21.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d5_incident_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d5_incident_2025-06-21.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d6_staff_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d6_staff_2025-07-01.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d7_funding_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d7_funding_2025-07-15.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def d8_memo_content(coralwind_corpus_path) -> str:
    file_path = os.path.abspath(os.path.join(coralwind_corpus_path, "d8_memo_2025-08-30.txt"))
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# --- Helper for mocking LLM ---
class MockLLMResponse:
    def __init__(self, json_output):
        self.json_output = json_output

    def invoke(self, input_data):
        # Simulate the structured_llm behavior
        return KnowledgeGraph.model_validate(self.json_output)

# --- Tests ---

def test_basic_extraction_with_alias_normalization(mocker, d1_news_content, mentions_data):
    """
    测试从 d1_news_2025-03-12.txt 进行基本提取，并进行别名规范化。
    验证关键实体和关系是否存在，并检查别名是否已规范化。
    """
    # Mock the LLM call to return a predictable graph for d1_news_content
    # This mock output should reflect what we expect the LLM to extract from d1_news_content
    # and include entities that will be normalized by mentions_data.
    mock_graph_output = {
                    "nodes": [
                        {"id": "珊瑚湾市政府", "type": "Government"},
                        {"id": "南海电力集团", "type": "Organization"},
                        {"id": "NPG", "type": "Organization"}, # Alias for 南海电力集团
                        {"id": "蓝珊研究所", "type": "Organization"},
                        {"id": "BCRI", "type": "Organization"}, # Alias for 蓝珊研究所
                        {"id": "海曦一号", "type": "Project"},
                        {"id": "周启明（NPG）", "type": "Person"}, # Changed from "周启明"
                        {"id": "2.4亿元", "type": "Value"},
                        {"id": "0.6亿元", "type": "Value"},
                        {"id": "0.2亿元", "type": "Value"},
                        {"id": "3.2亿元", "type": "Value"}
                    ],
                    "relationships": [
                        {
                            "source": {"id": "珊瑚湾市政府", "type": "Government"},
                            "target": {"id": "南海电力集团", "type": "Organization"},
                            "type": "partner_with",
                            "evidence": [{"doc": "d1", "sents": [1]}],
                            "confidence": 0.85
                        },
                        {
                            "source": {"id": "南海电力集团", "type": "Organization"},
                            "target": {"id": "蓝珊研究所", "type": "Organization"},
                            "type": "partner_with",
                            "evidence": [{"doc": "d1", "sents": [1]}],
                            "confidence": 0.86
                        },
                        {
                            "source": {"id": "南海电力集团", "type": "Organization"},
                            "target": {"id": "海曦一号", "type": "Project"},
                            "type": "funds",
                            "qualifiers": {"amount": "2.4亿元", "date": "2025-03-12"},
                            "evidence": [{"doc": "d1", "sents": [2]}],
                            "confidence": 0.84
                        },
                        {
                            "source": {"id": "珊瑚湾市政府", "type": "Government"},
                            "target": {"id": "海曦一号", "type": "Project"},
                            "type": "funds",
                            "qualifiers": {"amount": "0.6亿元", "date": "2025-03-12"},
                            "evidence": [{"doc": "d1", "sents": [2]}],
                            "confidence": 0.80
                        },
                        {
                            "source": {"id": "周启明（NPG）", "type": "Person"}, # Changed from "周启明"
                            "target": {"id": "海曦一号", "type": "Project"},
                            "type": "manages",
                            "qualifiers": {"role": "项目经理"},
                            "evidence": [{"doc": "d1", "sents": [5]}],
                            "confidence": 0.83
                        },
                        {
                            "source": {"id": "NPG", "type": "Organization"}, # Alias in source
                            "target": {"id": "BCRI", "type": "Organization"}, # Alias in target
                            "type": "partner_with",
                            "evidence": [{"doc": "d1", "sents": [1]}],
                            "confidence": 0.87
                        }
                    ],        "metadata": {
            "source": "d1_news_2025-03-12.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d1",
            "doc_date": "2025-03-12"
        }
    }
    
    # Mock the LLM and its structured output
    mock_llm = mocker.Mock()
    mock_structured_llm = mocker.Mock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mocker.patch('app.ChatGoogleGenerativeAI', return_value=mock_llm)
    
    # Mock the prompt object and its __or__ method
    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value = KnowledgeGraph.model_validate(mock_graph_output)

    mock_prompt_instance = mocker.Mock()
    # Correct way to mock a magic method's return value
    mock_prompt_instance.__or__ = mocker.Mock(return_value=mock_chain) 

    mocker.patch('app.ChatPromptTemplate.from_messages', return_value=mock_prompt_instance)

    # Ensure REL_SETS and PROMPT_TEMPLATE are loaded for the test
    mocker.patch.dict('app.REL_SETS', REL_SETS)
    mocker.patch('app.PROMPT_TEMPLATE', PROMPT_TEMPLATE)
    
    # Generate graph
    extracted_graph = generate_graph(
        text=d1_news_content,
        source="d1_news_2025-03-12.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d1",
        doc_date="2025-03-12"
    )

    assert isinstance(extracted_graph, KnowledgeGraph)
    assert len(extracted_graph.nodes) > 0
    assert len(extracted_graph.relationships) > 0

    # Normalize entities
    normalized_graph = normalize_entities(extracted_graph, mentions_data)

    # Assertions for normalized graph
    # Check if canonical IDs are used
    node_ids = {node.id for node in normalized_graph.nodes}
    assert "ORG.NPG" in node_ids
    assert "ORG.BCRI" in node_ids
    assert "ORG.GOV" in node_ids
    assert "PROJ.HX1" in node_ids
    assert "PER.ZQM_NPG" in node_ids # Assuming "周启明" from d1 is NPG's PM

    # Check that original aliases are gone
    assert "南海电力集团" not in node_ids # Should be normalized to ORG.NPG
    assert "NPG" not in node_ids # Should be normalized to ORG.NPG
    assert "蓝珊研究所" not in node_ids # Should be normalized to ORG.BCRI
    assert "BCRI" not in node_ids # Should be normalized to ORG.BCRI

    # Check relationships point to canonical IDs
    for rel in normalized_graph.relationships:
        assert rel.source.id in node_ids
        assert rel.target.id in node_ids
        # Example: Check a specific relationship after normalization
        if rel.type == "partner_with" and rel.source.id == "ORG.NPG" and rel.target.id == "ORG.BCRI":
            assert True # Found the normalized relationship
            break
    else:
        pytest.fail("Normalized 'partner_with' relationship between ORG.NPG and ORG.BCRI not found.")

    # Check node property merging (e.g., if "周启明" had a role property, it should be retained)
    zqm_node = next((node for node in normalized_graph.nodes if node.id == "PER.ZQM_NPG"), None)
    assert zqm_node is not None
    # The mock output doesn't have properties for 周启明 node itself, but for the relationship.
    # If the LLM were to output properties for the node, this is where we'd check for merging.
    # For now, we just check its existence.

    # Check metadata is preserved
    assert normalized_graph.metadata.doc_id == "d1"
    assert normalized_graph.metadata.doc_date == "2025-03-12"
    assert normalized_graph.metadata.source == "d1_news_2025-03-12.txt" # Corrected assertion

def test_temporal_qualification(mocker, d1_news_content, mentions_data):
    """
    测试时间限定的提取和规范化。
    验证关系中的日期限定符是否正确提取并格式化为ISO8601。
    """
    mock_graph_output = {
        "nodes": [
            {"id": "南海电力集团", "type": "Organization"},
            {"id": "海曦一号", "type": "Project"},
            {"id": "珊瑚湾市政府", "type": "Government"}
        ],
        "relationships": [
            {
                "source": {"id": "南海电力集团", "type": "Organization"},
                "target": {"id": "海曦一号", "type": "Project"},
                "type": "funds",
                "qualifiers": {"amount": "2.4亿元", "date": "2025-03-12"},
                "evidence": [{"doc": "d1", "sents": [2]}],
                "confidence": 0.84
            },
            {
                "source": {"id": "珊瑚湾市政府", "type": "Government"},
                "target": {"id": "海曦一号", "type": "Project"},
                "type": "funds",
                "qualifiers": {"amount": "0.6亿元", "date": "2025-03-12"},
                "evidence": [{"doc": "d1", "sents": [2]}],
                "confidence": 0.80
            }
        ],
        "metadata": {
            "source": "d1_news_2025-03-12.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d1",
            "doc_date": "2025-03-12"
        }
    }

    mock_llm = mocker.Mock()
    mock_structured_llm = mocker.Mock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mocker.patch('app.ChatGoogleGenerativeAI', return_value=mock_llm)
    
    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value = KnowledgeGraph.model_validate(mock_graph_output)

    mock_prompt_instance = mocker.Mock()
    mock_prompt_instance.__or__ = mocker.Mock(return_value=mock_chain) 

    mocker.patch('app.ChatPromptTemplate.from_messages', return_value=mock_prompt_instance)

    mocker.patch.dict('app.REL_SETS', REL_SETS)
    mocker.patch('app.PROMPT_TEMPLATE', PROMPT_TEMPLATE)

    extracted_graph = generate_graph(
        text=d1_news_content,
        source="d1_news_2025-03-12.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d1",
        doc_date="2025-03-12"
    )

    normalized_graph = normalize_entities(extracted_graph, mentions_data)

    # Assertions for temporal qualification
    found_temporal_relation = False
    for rel in normalized_graph.relationships:
        if rel.type == "funds" and rel.source.id == "ORG.NPG" and rel.target.id == "PROJ.HX1":
            assert rel.qualifiers is not None
            assert rel.qualifiers.get("date") == "2025-03-12"
            found_temporal_relation = True
            break
    assert found_temporal_relation, "Temporal qualification for 'funds' relation not found or incorrect."

def test_negation_rumor_clarification(mocker, d4_rumor_content, d5_incident_content, mentions_data):
    """
    测试否定和谣言澄清的提取。
    验证是否正确识别并表示了否定事实或谣言。
    """
    # Mock output for d4_rumor_content (rumor about whale stranding)
    mock_graph_output_rumor = {
        "nodes": [
            {"id": "鲸鱼搁浅", "type": "Event"},
            {"id": "珊瑚湾", "type": "Location"},
            {"id": "谣言", "type": "Concept"}
        ],
        "relationships": [
            {
                "source": {"id": "谣言", "type": "Concept"},
                "target": {"id": "鲸鱼搁浅", "type": "Event"},
                "type": "rumor_about",
                "evidence": [{"doc": "d4", "sents": [1]}],
                "confidence": 0.7
            }
        ],
        "metadata": {
            "source": "d4_rumor_2025-06-21.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d4",
            "doc_date": "2025-06-21"
        }
    }

    # Mock output for d5_incident_content (denial of whale stranding)
    mock_graph_output_denial = {
        "nodes": [
            {"id": "鲸鱼搁浅", "type": "Event"},
            {"id": "珊瑚湾生态环境局", "type": "GovernmentAgency"},
            {"id": "ORG.EEB", "type": "GovernmentAgency"} # Alias for 珊瑚湾生态环境局
        ],
        "relationships": [
            {
                "source": {"id": "珊瑚湾生态环境局", "type": "GovernmentAgency"},
                "target": {"id": "鲸鱼搁浅", "type": "Event"},
                "type": "negated:event_occurrence", # Example of negated relation
                "evidence": [{"doc": "d5", "sents": [1]}],
                "confidence": 0.95
            }
        ],
        "metadata": {
            "source": "d5_incident_2025-06-21.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d5",
            "doc_date": "2025-06-21"
        }
    }

    # Mock the LLM to return different outputs based on text input
    def mock_generate_graph_llm_output(input_dict):
        text_content = input_dict["text"]
        # Extract doc_id from the text content (assuming it's in the metadata line)
        match = re.search(r"id=(d\d+)", text_content)
        doc_id = match.group(1) if match else "unknown_doc"

        if doc_id == "d4":
            return KnowledgeGraph.model_validate(mock_graph_output_rumor)
        elif doc_id == "d5":
            return KnowledgeGraph.model_validate(mock_graph_output_denial)
        else:
            raise ValueError(f"Unexpected doc_id '{doc_id}' in mock_generate_graph_llm_output")

    mock_llm = mocker.Mock()
    mock_structured_llm = mocker.Mock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mocker.patch('app.ChatGoogleGenerativeAI', return_value=mock_llm)
    
    mock_chain = mocker.Mock()
    mock_chain.invoke.side_effect = mock_generate_graph_llm_output # Pass the function directly

    mock_prompt_instance = mocker.Mock()
    mock_prompt_instance.__or__ = mocker.Mock(return_value=mock_chain) 

    mocker.patch('app.ChatPromptTemplate.from_messages', return_value=mock_prompt_instance)

    mocker.patch.dict('app.REL_SETS', REL_SETS)
    mocker.patch('app.PROMPT_TEMPLATE', PROMPT_TEMPLATE)

    # Process rumor document
    extracted_graph_rumor = generate_graph(
        text=d4_rumor_content,
        source="d4_rumor_2025-06-21.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d4",
        doc_date="2025-06-21"
    )
    normalized_graph_rumor = normalize_entities(extracted_graph_rumor, mentions_data)

    # Assertions for rumor
    found_rumor_relation = False
    for rel in normalized_graph_rumor.relationships:
        if rel.type == "rumor_about" and rel.source.id == "谣言" and rel.target.id == "鲸鱼搁浅":
            found_rumor_relation = True
            break
    assert found_rumor_relation, "Rumor relation not found or incorrect."

    # Process denial document
    extracted_graph_denial = generate_graph(
        text=d5_incident_content,
        source="d5_incident_2025-06-21.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d5",
        doc_date="2025-06-21"
    )
    normalized_graph_denial = normalize_entities(extracted_graph_denial, mentions_data)

    # Assertions for denial
    found_negated_relation = False
    for rel in normalized_graph_denial.relationships:
        if rel.type == "negated:event_occurrence" and rel.source.id == "ORG.EEB" and rel.target.id == "鲸鱼搁浅":
            found_negated_relation = True
            break
    assert found_negated_relation, "Negated relation not found or incorrect."

def test_multi_hop_relationships(mocker, d1_news_content, d3_permit_content, mentions_data):
    """
    测试多跳关系的提取。
    验证是否可以从多个文档中推断出链式事实。
    """
    # Mock output for d1_news_content (initial facts)
    mock_graph_output_d1 = {
        "nodes": [
            {"id": "南海电力集团", "type": "Organization"},
            {"id": "海曦一号", "type": "Project"},
            {"id": "珊瑚湾市政府", "type": "Government"},
            {"id": "南礁珊瑚保护区", "type": "ProtectedArea"}
        ],
        "relationships": [
            {
                "source": {"id": "南海电力集团", "type": "Organization"},
                "target": {"id": "海曦一号", "type": "Project"},
                "type": "leads",
                "evidence": [{"doc": "d1", "sents": [5]}],
                "confidence": 0.8
            },
            {
                "source": {"id": "海曦一号", "type": "Project"},
                "target": {"id": "南礁珊瑚保护区", "type": "ProtectedArea"},
                "type": "nearby",
                "evidence": [{"doc": "d1", "sents": [6]}],
                "confidence": 0.75
            }
        ],
        "metadata": {
            "source": "d1_news_2025-03-12.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d1",
            "doc_date": "2025-03-12"
        }
    }

    # Mock output for d3_permit_content (additional facts for multi-hop)
    mock_graph_output_d3 = {
        "nodes": [
            {"id": "南礁珊瑚保护区", "type": "ProtectedArea"},
            {"id": "珊瑚湾市", "type": "City"},
            {"id": "ORG.EEB", "type": "GovernmentAgency"} # Alias for 珊瑚湾生态环境局
        ],
        "relationships": [
            {
                "source": {"id": "南礁珊瑚保护区", "type": "ProtectedArea"},
                "target": {"id": "珊瑚湾市", "type": "City"},
                "type": "located_in",
                "evidence": [{"doc": "d3", "sents": [1]}],
                "confidence": 0.9
            },
            {
                "source": {"id": "ORG.EEB", "type": "GovernmentAgency"},
                "target": {"id": "南礁珊瑚保护区", "type": "ProtectedArea"},
                "type": "manages",
                "evidence": [{"doc": "d3", "sents": [2]}],
                "confidence": 0.85
            }
        ],
        "metadata": {
            "source": "d3_permit_2025-06-10.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d3",
            "doc_date": "2025-06-10"
        }
    }

    def mock_generate_graph_llm_output_multi_hop(input_dict):
        text_content = input_dict["text"]
        match = re.search(r"id=(d\d+)", text_content)
        doc_id = match.group(1) if match else "unknown_doc"

        if doc_id == "d1":
            return KnowledgeGraph.model_validate(mock_graph_output_d1)
        elif doc_id == "d3":
            return KnowledgeGraph.model_validate(mock_graph_output_d3)
        else:
            raise ValueError(f"Unexpected doc_id '{doc_id}' in mock_generate_graph_llm_output_multi_hop")

    mock_llm = mocker.Mock()
    mock_structured_llm = mocker.Mock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mocker.patch('app.ChatGoogleGenerativeAI', return_value=mock_llm)
    
    mock_chain = mocker.Mock()
    mock_chain.invoke.side_effect = mock_generate_graph_llm_output_multi_hop

    mock_prompt_instance = mocker.Mock()
    mock_prompt_instance.__or__ = mocker.Mock(return_value=mock_chain) 

    mocker.patch('app.ChatPromptTemplate.from_messages', return_value=mock_prompt_instance)

    mocker.patch.dict('app.REL_SETS', REL_SETS)
    mocker.patch('app.PROMPT_TEMPLATE', PROMPT_TEMPLATE)

    # Process d1 document
    extracted_graph_d1 = generate_graph(
        text=d1_news_content,
        source="d1_news_2025-03-12.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d1",
        doc_date="2025-03-12"
    )
    
    # Process d3 document
    extracted_graph_d3 = generate_graph(
        text=d3_permit_content,
        source="d3_permit_2025-06-10.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d3",
        doc_date="2025-06-10"
    )

    # Aggregate and normalize
    all_graphs = [extracted_graph_d1, extracted_graph_d3]
    aggregated_nodes = []
    aggregated_relationships = []
    for graph in all_graphs:
        aggregated_nodes.extend(graph.nodes)
        aggregated_relationships.extend(graph.relationships)
    
    aggregated_graph = KnowledgeGraph(
        nodes=aggregated_nodes,
        relationships=aggregated_relationships,
        metadata=Metadata(source="聚合图谱", timestamp=datetime.now().isoformat())
    )
    normalized_graph = normalize_entities(aggregated_graph, mentions_data)

    # Assertions for multi-hop relationships
    # Check for the inferred path: 海曦一号 -> nearby -> 南礁珊瑚保护区 -> located_in -> 珊瑚湾市
    found_path_step1 = False
    found_path_step2 = False

    for rel in normalized_graph.relationships:
        if rel.type == "nearby" and rel.source.id == "PROJ.HX1" and rel.target.id == "LOC.NANCHAO":
            found_path_step1 = True
        if rel.type == "located_in" and rel.source.id == "LOC.NANCHAO" and rel.target.id == "LOC.CHB":
            found_path_step2 = True
    
    assert found_path_step1, "First step of multi-hop path (PROJ.HX1 nearby LOC.NANCHAO) not found."
    assert found_path_step2, "Second step of multi-hop path (LOC.NANCHAO located_in LOC.CHB) not found."

    # Also check for the ORG.EEB manages LOC.NANCHAO relationship
    found_manages_relation = False
    for rel in normalized_graph.relationships:
        if rel.type == "manages" and rel.source.id == "ORG.EEB" and rel.target.id == "LOC.NANCHAO":
            found_manages_relation = True
            break
    assert found_manages_relation, "ORG.EEB manages LOC.NANCHAO relation not found."

def test_event_quantity_aggregation(mocker, d2_brief_content, d7_funding_content, mentions_data):
    """
    测试事件和数量聚合的提取。
    验证是否可以从多个文档中正确聚合数值信息。
    """
    # Mock output for d2_brief_content (initial funding)
    mock_graph_output_d2 = {
        "nodes": [
            {"id": "海曦一号", "type": "Project"},
            {"id": "南海电力集团", "type": "Organization"},
            {"id": "珊瑚湾市政府", "type": "Government"}
        ],
        "relationships": [
            {
                "source": {"id": "南海电力集团", "type": "Organization"},
                "target": {"id": "海曦一号", "type": "Project"},
                "type": "funds",
                "qualifiers": {"amount": "2.4亿元", "date": "2025-03-12"},
                "evidence": [{"doc": "d2", "sents": [2]}],
                "confidence": 0.85
            },
            {
                "source": {"id": "珊瑚湾市政府", "type": "Government"},
                "target": {"id": "海曦一号", "type": "Project"},
                "type": "funds",
                "qualifiers": {"amount": "0.6亿元", "date": "2025-03-12"},
                "evidence": [{"doc": "d2", "sents": [2]}],
                "confidence": 0.80
            }
        ],
        "metadata": {
            "source": "d2_brief_2025-05-01.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d2",
            "doc_date": "2025-05-01"
        }
    }

    # Mock output for d7_funding_content (additional funding)
    mock_graph_output_d7 = {
        "nodes": [
            {"id": "海曦一号", "type": "Project"},
            {"id": "青岚大学", "type": "Organization"},
            {"id": "QLU", "type": "Organization"} # Alias for 青岚大学
        ],
        "relationships": [
            {
                "source": {"id": "青岚大学", "type": "Organization"},
                "target": {"id": "海曦一号", "type": "Project"},
                "type": "funds",
                "qualifiers": {"amount": "1.0亿元", "date": "2025-07-15"},
                "evidence": [{"doc": "d7", "sents": [1]}],
                "confidence": 0.9
            }
        ],
        "metadata": {
            "source": "d7_funding_2025-07-15.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d7",
            "doc_date": "2025-07-15"
        }
    }

    def mock_generate_graph_llm_output_aggregation(input_dict):
        text_content = input_dict["text"]
        match = re.search(r"id=(d\d+)", text_content)
        doc_id = match.group(1) if match else "unknown_doc"

        if doc_id == "d2":
            return KnowledgeGraph.model_validate(mock_graph_output_d2)
        elif doc_id == "d7":
            return KnowledgeGraph.model_validate(mock_graph_output_d7)
        else:
            raise ValueError(f"Unexpected doc_id '{doc_id}' in mock_generate_graph_llm_output_aggregation")

    mock_llm = mocker.Mock()
    mock_structured_llm = mocker.Mock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mocker.patch('app.ChatGoogleGenerativeAI', return_value=mock_llm)
    
    mock_chain = mocker.Mock()
    mock_chain.invoke.side_effect = mock_generate_graph_llm_output_aggregation

    mock_prompt_instance = mocker.Mock()
    mock_prompt_instance.__or__ = mocker.Mock(return_value=mock_chain) 

    mocker.patch('app.ChatPromptTemplate.from_messages', return_value=mock_prompt_instance)

    mocker.patch.dict('app.REL_SETS', REL_SETS)
    mocker.patch('app.PROMPT_TEMPLATE', PROMPT_TEMPLATE)

    # Process d2 document
    extracted_graph_d2 = generate_graph(
        text=d2_brief_content,
        source="d2_brief_2025-05-01.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d2",
        doc_date="2025-05-01"
    )
    
    # Process d7 document
    extracted_graph_d7 = generate_graph(
        text=d7_funding_content,
        source="d7_funding_2025-07-15.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d7",
        doc_date="2025-07-15"
    )

    # Aggregate and normalize
    all_graphs = [extracted_graph_d2, extracted_graph_d7]
    aggregated_nodes = []
    aggregated_relationships = []
    for graph in all_graphs:
        aggregated_nodes.extend(graph.nodes)
        aggregated_relationships.extend(graph.relationships)
    
    aggregated_graph = KnowledgeGraph(
        nodes=aggregated_nodes,
        relationships=aggregated_relationships,
        metadata=Metadata(source="聚合图谱", timestamp=datetime.now().isoformat())
    )
    normalized_graph = normalize_entities(aggregated_graph, mentions_data)

    # Assertions for event and quantity aggregation
    # Check if the total funding for PROJ.HX1 is correctly represented
    # This requires the LLM to aggregate, which is not directly tested by this mock.
    # Instead, we check if individual funding events are present and normalized.
    
    found_npg_funding = False
    found_gov_funding = False
    found_qlu_funding = False

    for rel in normalized_graph.relationships:
        if rel.type == "funds" and rel.target.id == "PROJ.HX1":
            if rel.source.id == "ORG.NPG" and rel.qualifiers and rel.qualifiers.get("amount") == "2.4亿元":
                found_npg_funding = True
            if rel.source.id == "ORG.GOV" and rel.qualifiers and rel.qualifiers.get("amount") == "0.6亿元":
                found_gov_funding = True
            if rel.source.id == "ORG.QLU" and rel.qualifiers and rel.qualifiers.get("amount") == "1.0亿元":
                found_qlu_funding = True
    
    assert found_npg_funding, "NPG funding for PROJ.HX1 not found or incorrect."
    assert found_gov_funding, "Government funding for PROJ.HX1 not found or incorrect."
    assert found_qlu_funding, "QLU funding for PROJ.HX1 not found or incorrect."

    # Check that aliases are normalized
    node_ids = {node.id for node in normalized_graph.nodes}
    assert "ORG.QLU" in node_ids
    assert "青岚大学" not in node_ids
    assert "QLU" not in node_ids

def test_conflict_disambiguation(mocker, d6_staff_content, d8_memo_content, mentions_data):
    """
    测试冲突与消歧的提取。
    验证系统如何处理冲突信息，特别是当存在权威来源排序时。
    """
    # Mock output for d6_staff_content (initial role for 周启明)
    mock_graph_output_d6 = {
        "nodes": [
            {"id": "周启明（NPG）", "type": "Person"},
            {"id": "南海电力集团", "type": "Organization"},
            {"id": "项目经理", "type": "Role"}
        ],
        "relationships": [
            {
                "source": {"id": "周启明（NPG）", "type": "Person"},
                "target": {"id": "南海电力集团", "type": "Organization"},
                "type": "holds_role",
                "qualifiers": {"role": "项目经理", "since": "2025-07-01"},
                "evidence": [{"doc": "d6", "sents": [1]}],
                "confidence": 0.88
            }
        ],
        "metadata": {
            "source": "d6_staff_2025-07-01.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d6",
            "doc_date": "2025-07-01"
        }
    }

    # Mock output for d8_memo_content (conflicting role for 周启明, higher authority)
    mock_graph_output_d8 = {
        "nodes": [
            {"id": "周启明（副市长）", "type": "Person"},
            {"id": "珊瑚湾市政府", "type": "Government"},
            {"id": "副市长", "type": "Role"}
        ],
        "relationships": [
            {
                "source": {"id": "周启明（副市长）", "type": "Person"},
                "target": {"id": "珊瑚湾市政府", "type": "Government"},
                "type": "holds_role",
                "qualifiers": {"role": "副市长", "since": "2025-08-30"},
                "evidence": [{"doc": "d8", "sents": [1]}],
                "confidence": 0.95 # Higher confidence/authority
            }
        ],
        "metadata": {
            "source": "d8_memo_2025-08-30.txt",
            "timestamp": datetime.now().isoformat(),
            "doc_id": "d8",
            "doc_date": "2025-08-30"
        }
    }

    def mock_generate_graph_llm_output_conflict(input_dict):
        text_content = input_dict["text"]
        match = re.search(r"id=(d\d+)", text_content)
        doc_id = match.group(1) if match else "unknown_doc"

        if doc_id == "d6":
            return KnowledgeGraph.model_validate(mock_graph_output_d6)
        elif doc_id == "d8":
            return KnowledgeGraph.model_validate(mock_graph_output_d8)
        else:
            raise ValueError(f"Unexpected doc_id '{doc_id}' in mock_generate_graph_llm_output_conflict")

    mock_llm = mocker.Mock()
    mock_structured_llm = mocker.Mock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mocker.patch('app.ChatGoogleGenerativeAI', return_value=mock_llm)
    
    mock_chain = mocker.Mock()
    mock_chain.invoke.side_effect = mock_generate_graph_llm_output_conflict

    mock_prompt_instance = mocker.Mock()
    mock_prompt_instance.__or__ = mocker.Mock(return_value=mock_chain) 

    mocker.patch('app.ChatPromptTemplate.from_messages', return_value=mock_prompt_instance)

    mocker.patch.dict('app.REL_SETS', REL_SETS)
    mocker.patch('app.PROMPT_TEMPLATE', PROMPT_TEMPLATE)

    # Process d6 document
    extracted_graph_d6 = generate_graph(
        text=d6_staff_content,
        source="d6_staff_2025-07-01.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d6",
        doc_date="2025-07-01"
    )
    
    # Process d8 document
    extracted_graph_d8 = generate_graph(
        text=d8_memo_content,
        source="d8_memo_2025-08-30.txt",
        model_name="gemini-2.5-pro",
        node_color="#FFADAD",
        edge_color="#9BF6FF",
        rel_set_name="GraphRAG-RELSET-GenericWeb-zh",
        doc_id="d8",
        doc_date="2025-08-30"
    )

    # Aggregate and normalize
    all_graphs = [extracted_graph_d6, extracted_graph_d8]
    aggregated_nodes = []
    aggregated_relationships = []
    for graph in all_graphs:
        aggregated_nodes.extend(graph.nodes)
        aggregated_relationships.extend(graph.relationships)
    
    aggregated_graph = KnowledgeGraph(
        nodes=aggregated_nodes,
        relationships=aggregated_relationships,
        metadata=Metadata(source="聚合图谱", timestamp=datetime.now().isoformat())
    )
    normalized_graph = normalize_entities(aggregated_graph, mentions_data)

    # Assertions for conflict and disambiguation
    # Check for both "周启明" entities (NPG Project Manager and Vice Mayor)
    node_ids = {node.id for node in normalized_graph.nodes}
    assert "PER.ZQM_NPG" in node_ids
    assert "PER.ZQM_VCM" in node_ids

    # Check that both roles are present, as the current system extracts all facts.
    # Disambiguation based on authority is handled by the prompt, not post-processing here.
    found_npg_role = False
    found_vcm_role = False

    for rel in normalized_graph.relationships:
        if rel.type == "holds_role":
            if rel.source.id == "PER.ZQM_NPG" and rel.target.id == "ORG.NPG" and rel.qualifiers and rel.qualifiers.get("role") == "项目经理":
                found_npg_role = True
            if rel.source.id == "PER.ZQM_VCM" and rel.target.id == "ORG.GOV" and rel.qualifiers and rel.qualifiers.get("role") == "副市长":
                found_vcm_role = True
    
    assert found_npg_role, "PER.ZQM_NPG holds_role Project Manager not found."
    assert found_vcm_role, "PER.ZQM_VCM holds_role Vice Mayor not found."

    # Further checks could involve verifying confidence scores or evidence to see if
    # the system prioritizes one over the other based on AUTHORITY_ORDER, but this
    # would require more sophisticated mocking of the LLM's output based on prompt logic.