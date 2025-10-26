import os
import time
import re
import streamlit as st
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from pyvis.network import Network
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Import parsers for different file types
from PyPDF2 import PdfReader
import docx
from odf.opendocument import load as load_odt
from odf import text as odf_text, teletype as odf_teletype
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

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

def is_youtube_url(url: str) -> bool:
    """Checks if a string is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return re.match(youtube_regex, url) is not None

def get_text_from_youtube(url: str) -> str:
    """Extracts the transcript from a YouTube video URL."""
    try:
        video_id_match = re.search(r'(v=|/)([\w-]+)', url)
        if not video_id_match:
            st.error("无法从URL中提取有效的YouTube视频ID。")
            return ""
        video_id = video_id_match.group(2)
        
        # Correctly instantiate the class and then call the method
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Find a transcript in the preferred languages
        try:
            transcript = transcript_list.find_transcript(['zh-Hans', 'zh-Hant', 'en'])
        except NoTranscriptFound:
            # If no manual transcript is found, try to find a generated one
            try:
                transcript = transcript_list.find_generated_transcript(['zh-Hans', 'zh-Hant', 'en'])
            except NoTranscriptFound:
                st.error(f"视频 {video_id} 未找到中文或英文字幕。")
                return ""

        # Fetch the actual transcript data and join the text
        full_transcript = " ".join([item['text'] for item in transcript.fetch()])
        return full_transcript

    except Exception as e:
        st.error(f"获取YouTube字幕时发生错误: {e}")
        return ""

def get_text_from_file(uploaded_file) -> str:
    """Extracts plain text from an uploaded file based on its extension."""
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        text = ""

        if file_extension == ".pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        elif file_extension == ".docx":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text

        elif file_extension == ".odt":
            doc = load_odt(uploaded_file)
            all_paras = doc.getElementsByType(odf_text.P)
            for para in all_paras:
                text += odf_teletype.extractText(para) + "\n"
            return text
        
        elif file_extension in [".html", ".htm"]:
            return BeautifulSoup(uploaded_file.read(), "html.parser").get_text()
        
        elif file_extension == ".md":
            md_text = uploaded_file.read().decode("utf-8")
            # Basic markdown removal
            text = re.sub(r'[\*\#\`\>]', '', md_text)
            return text

        elif file_extension == ".txt":
            return uploaded_file.read().decode("utf-8")

        else:
            st.warning(f"不支持的文件格式: {file_extension}")
            return ""
            
    except Exception as e:
        st.error(f"解析文件时发生错误: {e}")
        return ""

def generate_graph(text: str) -> KnowledgeGraph:
    """Generates a knowledge graph from a given text."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(KnowledgeGraph)
    
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

text_input = st.text_area("粘贴文本（或输入YouTube链接）:")
uploaded_file = st.file_uploader(
    "或者上传一个文件", 
    type=['txt', 'pdf', 'docx', 'md', 'html', 'htm', 'odt']
)

generate_button = st.button("生成图谱")

if generate_button:
    if not GOOGLE_API_KEY:
        st.error("未找到 GOOGLE_API_KEY。请确保您的 .env 文件已正确设置。")
    
    text_to_process = ""
    source_type = ""

    # Determine the source of text to be processed
    if text_input:
        if is_youtube_url(text_input):
            source_type = "youtube"
        else:
            source_type = "text"
    elif uploaded_file:
        source_type = "file"

    if not source_type:
        st.warning("请输入文本、YouTube链接或上传文件。")
    else:
        # --- Progress Bar & Graph Generation ---
        progress_bar = st.progress(0, text="正在初始化...")
        
        try:
            # Step 1: Get text from source
            if source_type == "youtube":
                progress_bar.progress(5, text=f"正在获取YouTube字幕...")
                text_to_process = get_text_from_youtube(text_input)
            elif source_type == "file":
                progress_bar.progress(5, text=f"正在解析文件...")
                text_to_process = get_text_from_file(uploaded_file)
            else: # plain text
                text_to_process = text_input

            if not text_to_process:
                progress_bar.empty()
            else:
                time.sleep(0.2) # Short delay for UX
                progress_bar.progress(10, text="正在调用大语言模型... (这可能需要一些时间)")
                graph = generate_graph(text_to_process)

                progress_bar.progress(90, text="已获取数据，正在渲染图谱...")
                time.sleep(0.2) # Short delay for UX

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
                        
                        title = node.model_dump_json(indent=2)
                        
                        net.add_node(node.id, label=node.id, title=title, color=color)

                    # Add edges with detailed tooltips
                    for edge in graph.relationships:
                        edge_type = edge.type
                        if edge_type not in type_color_map:
                            type_color_map[edge_type] = palette[color_index % len(palette)]
                            color_index += 1
                        color = type_color_map[edge_type]

                        title = edge.model_dump_json(indent=2)

                        net.add_edge(edge.source.id, edge.target.id, label=edge.type, color=color, title=title)

                    # Save graph to a temporary file and display
                    graph_html_path = "temp_graph.html"
                    net.save_graph(graph_html_path)
                    
                    with open(graph_html_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    
                    progress_bar.progress(100)
                    st.success("图谱生成成功！")
                    components.html(html_content, height=620)
                    
                    # Clean up the temporary file
                    if os.path.exists(graph_html_path):
                        os.remove(graph_html_path)
                else:
                    progress_bar.progress(100)
                    st.warning("未能从文本中提取出任何实体和关系。")
                
                progress_bar.empty() # Clear the progress bar

        except Exception as e:
            progress_bar.empty() # Clear the progress bar on error too
            st.error(f"生成图谱时发生错误: {e}")
