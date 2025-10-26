import os
import streamlit as st
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from pyvis.network import Network
import streamlit.components.v1 as components
from dotenv import load_dotenv

# --- CONFIGURATION ---

__version__ = "0.1.0"

st.set_page_config(page_title="文本知识图谱提取器")

# Load API Key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Pydantic Models for Graph Structure ---

class Node(BaseModel):
    """Represents a node in the knowledge graph."""
    id: str = Field(..., description="Unique identifier for the node.")
    type: str = Field("Unknown", description="The type or label of the node.")
    properties: Optional[dict] = Field(None, description="Additional properties of the node.")

class Relationship(BaseModel):
    """Represents a relationship between two nodes in the knowledge graph."""
    source: Node = Field(..., description="The source node of the relationship.")
    target: Node = Field(..., description="The target node of the relationship.")
    type: str = Field(..., description="The type of the relationship.")
    properties: Optional[dict] = Field(None, description="Additional properties of the relationship.")

class KnowledgeGraph(BaseModel):
    """Represents the entire knowledge graph."""
    nodes: List[Node] = Field(..., description="List of all nodes in the graph.")
    relationships: List[Relationship] = Field(..., description="List of all relationships in the graph.")

# --- MODEL INITIALIZATION ---

@st.cache_resource
def get_llm():
    """Initializes and caches the LLM."""
    return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, google_api_key=GOOGLE_API_KEY)

# --- CORE LOGIC ---

def generate_graph(text: str) -> KnowledgeGraph:
    """Generates a knowledge graph from a given text."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(KnowledgeGraph)
    
    # Updated prompt to handle bi-directional relationships
    prompt = f"""从以下文本中提取知识图谱。请识别出所有的实体作为节点，以及它们之间的关系。
    确保节点具有唯一的ID（通常是实体的名称）和类型（例如：人、地点、组织、概念）。
    如果实体或关系有额外的属性（例如日期、数量、职位、事件描述等），请将它们提取到'properties'字段中。
    特别地，如果关系是双向的（例如‘合作’、‘同事’、‘配偶’），请为每个方向都生成一条关系边（例如 A-合作->B 和 B-合作->A）。
    文本: {text}
    """
    
    graph = structured_llm.invoke(prompt)
    return graph

# --- UI & VISUALIZATION ---

st.title("文本知识图谱提取器")
st.caption(f"Version {__version__}")
st.caption("从文本中提取知识图谱并进行可视化。")

text_input = st.text_area("粘贴文本:")
uploaded_file = st.file_uploader("或者上传一个 .txt 文件", type="txt")
generate_button = st.button("生成图谱")

if generate_button:
    if not GOOGLE_API_KEY:
        st.error("未找到 GOOGLE_API_KEY。请确保您的 .env 文件已正确设置。")
    elif not text_input and not uploaded_file:
        st.warning("请输入文本或上传文件。")
    else:
        with st.spinner("正在生成图谱..."):
            # Determine text source
            if uploaded_file:
                text = uploaded_file.read().decode("utf-8")
            else:
                text = text_input

            try:
                graph = generate_graph(text)

                # Visualize the graph
                if graph.nodes:
                    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", notebook=True, directed=True)
                    
                    palette = ["#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF", "#BDB2FF", "#FFC6FF"]
                    type_color_map = {}
                    color_index = 0

                    # Add nodes with detailed tooltips
                    for node in graph.nodes:
                        node_type = node.type
                        if node_type not in type_color_map:
                            type_color_map[node_type] = palette[color_index % len(palette)]
                            color_index += 1
                        color = type_color_map[node_type]
                        
                        title = f"Type: {node.type}"
                        if node.properties:
                            props_str = "\n".join([f"{k}: {v}" for k, v in node.properties.items()])
                            title += f"\nProperties:\n{props_str}"
                        
                        net.add_node(node.id, label=node.id, title=title, color=color)

                    # Add edges with detailed tooltips
                    for edge in graph.relationships:
                        edge_type = edge.type
                        if edge_type not in type_color_map:
                            type_color_map[edge_type] = palette[color_index % len(palette)]
                            color_index += 1
                        color = type_color_map[edge_type]

                        title = f"Type: {edge.type}"
                        if edge.properties:
                            props_str = "\n".join([f"{k}: {v}" for k, v in edge.properties.items()])
                            title += f"\nProperties:\n{props_str}"

                        net.add_edge(edge.source.id, edge.target.id, label=edge.type, color=color, title=title)

                    # Save graph to a temporary file and display
                    graph_html_path = "temp_graph.html"
                    net.save_graph(graph_html_path)
                    
                    with open(graph_html_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    
                    st.success("图谱生成成功！")
                    components.html(html_content, height=620)
                    
                    # Clean up the temporary file
                    if os.path.exists(graph_html_path):
                        os.remove(graph_html_path)
                else:
                    st.warning("未能从文本中提取出任何实体和关系。")

            except Exception as e:
                st.error(f"生成图谱时发生错误: {e}")
