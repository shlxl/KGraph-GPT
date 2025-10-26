# 文本知识图谱提取器 (Knowledge Graph Extractor)

[![version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://semver.org)

这是一个使用 Streamlit 构建的Web应用程序，旨在从多种来源（包括纯文本、各种格式的文档以及YouTube视频）中提取知识图谱，并将其进行交互式可视化。

This is a web application built with Streamlit, designed to extract knowledge graphs from various sources (including plain text, documents of different formats, and YouTube videos) and visualize them interactively.

---

## 📖 中文说明

### ✨ 功能特性

- **多源输入**: 
  - **文本/链接输入**: 支持直接在文本框中粘贴大段文本，或输入一个 **YouTube 视频链接**来提取其字幕内容。
  - **多格式文件上传**: 允许用户上传多种主流格式的文件，包括 `.txt`, `.pdf`, `.docx`, `.odt`, `.html`, `.md`。
- **智能提取**: 利用 Google Gemini 2.5 Pro 模型强大的自然语言理解能力，自动识别和提取文本中的实体（Nodes）、关系（Relationships）以及它们的详细属性（Properties）。
- **智能关系处理**: 能够理解并处理“合作”等**双向关系**，在图谱中生成两条方向相反的边来表示。
- **交互式可视化**: 
  - 使用 Pyvis 库生成一个可缩放、可拖拽的交互式网络图。
  - **自动着色**: 根据节点和边的类型自动分配不同的颜色，使图谱结构更清晰。
  - **方向显示**: 关系“边”带有箭头，明确表示其方向。
  - **详细元数据**: 鼠标悬停在任何节点或边上，都会显示其包含所有信息的完整 **JSON 元数据**。
- **用户体验**: 
  - 在处理长文本或视频时，提供**模拟进度条**和状态提示，优化等待体验。
- **自动化测试**: 项目包含一套使用 `pytest` 编写的单元测试和集成测试，确保核心功能的稳定可靠。

### 🛠️ 技术栈

- **Web框架**: Streamlit
- **大语言模型 (LLM)**: Google Gemini 2.5 Pro
- **核心框架**: Langchain
- **图谱可视化**: Pyvis
- **文件解析**: PyPDF2, python-docx, odfpy, BeautifulSoup4
- **YouTube 字幕**: youtube-transcript-api
- **测试框架**: pytest, pytest-mock

### 🚀 安装与启动

**1. 准备环境**

- 克隆或下载项目到本地。
- 在项目根目录下，创建一个名为 `.env` 的文件，并填入您的 Google API 密钥：
  ```
  GOOGLE_API_KEY="YOUR_API_KEY_HERE"
  ```
  请将 `YOUR_API_KEY_HERE` 替换为您真实的 Google API 密钥。

**2. 安装依赖**

在项目根目录下，执行以下命令来创建虚拟环境并安装所有必需的 Python 依赖包：

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**3. 运行应用**

确保虚拟环境已激活，然后在项目根目录下执行以下命令：

```bash
streamlit run app.py
```

应用启动后，浏览器将自动打开一个新的标签页，地址通常为 `http://localhost:8501`。

### 🚢 部署 (Deployment)

本项目使用 Docker Compose 来统一管理和启动 Neo4j 服务，极大地方便了部署。

**1. 前提条件**

- 一台安装了 `Docker` 和 `docker-compose` 的服务器。

**2. 配置**

- 将项目克隆到您的服务器上。
- **重要**: 编辑 `docker-compose.yaml` 文件，将 `NEO4J_AUTH` 环境变量中的 `your_strong_password_here` 替换为您自己的一个强密码。
- 创建一个 `.env` 文件，填入您的 `GOOGLE_API_KEY` 和您刚刚在 `docker-compose.yaml` 中设置的 `NEO4J_PASSWORD`。两个文件的密码必须完全一致。
  ```
  GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
  NEO4J_URI="neo4j://localhost:7687"
  NEO4J_USER="neo4j"
  NEO4J_PASSWORD="your_strong_password_here"
  ```

**3. 启动服务**

在项目根目录下，执行以下命令来启动 Neo4j 数据库服务：

```bash
docker-compose up -d
```
这个命令会以后台模式启动 Neo4j 数据库。

**4. 启动应用**

接着，在同目录下（需要先按“安装与启动”章节的方式创建并激活虚拟环境）启动 Streamlit 应用：

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**5. 访问**
- **应用界面**: `http://<您的服务器IP>:8501`
- **Neo4j 浏览器**: `http://<您的服务器IP>:7474` (您可以在这里查看和查询已存入的图谱数据)

### 📖 如何使用

1.  **输入文本**: 在文本框中输入您想要分析的文字，或者直接粘贴一个 **YouTube 视频链接**。
2.  **或上传文件**: 点击 "或者上传一个文件" 按钮，选择一个本地支持格式的文件（如 PDF, DOCX 等）。
3.  **生成图谱**: 点击 "生成图谱" 按钮。
4.  **查看结果**: 等待进度条走完，应用下方会显示一个可交互的知识图谱。您可以拖动节点，缩放画布，并将鼠标悬停在节点或边上以查看其完整的元数据。

### 🧪 如何测试

本项目配置了自动化测试。在安装完所有依赖后，您可以在项目根目录下运行：

```bash
pytest
```

---

## English Description

### ✨ Features

- **Multi-Source Input**: 
  - **Text/Link Input**: Supports pasting large blocks of text or a **YouTube video link** to extract its transcript.
  - **Multi-Format File Upload**: Supports various file formats including `.txt`, `.pdf`, `.docx`, `.odt`, `.html`, and `.md`.
- **Intelligent Extraction**: Leverages Google's Gemini 2.5 Pro model to automatically identify and extract entities (Nodes), relationships (Relationships), and their detailed properties.
- **Smart Relationship Handling**: Capable of understanding and processing **bi-directional relationships** (e.g., collaboration), generating reciprocal edges in the graph.
- **Interactive Visualization**: 
  - Generates a zoomable, draggable graph using Pyvis.
  - **Auto-Coloring**: Automatically assigns different colors to nodes and edges based on their type.
  - **Directed Edges**: Edges are displayed with arrows to indicate direction.
  - **Detailed Metadata**: Hovering over any node or edge reveals its complete **JSON metadata** in a tooltip.
- **User Experience**: 
  - Provides a **simulated progress bar** with status text during processing.
- **Automated Testing**: Includes a test suite using `pytest` for unit and integration testing, ensuring the reliability of core functionalities.

### 🛠️ Tech Stack

- **Web Framework**: Streamlit
- **LLM**: Google Gemini 2.5 Pro
- **Core Framework**: Langchain
- **Graph Visualization**: Pyvis
- **File Parsers**: PyPDF2, python-docx, odfpy, BeautifulSoup4
- **YouTube Transcript**: youtube-transcript-api
- **Testing Framework**: pytest, pytest-mock

### 🚀 Installation & Running

**1. Setup Environment**

- Clone or download the project.
- In the project root directory, create a file named `.env` and add your Google API key:
  ```
  GOOGLE_API_KEY="YOUR_API_KEY_HERE"
  ```

**2. Install Dependencies**

In the project root, run the following commands to create a virtual environment and install dependencies:

```bash
# Create venv
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Run the App**

With the virtual environment activated, run the following command in the project root:

```bash
streamlit run app.py
```

### 🚢 Deployment

This project uses Docker Compose to manage and launch the Neo4j service, which greatly simplifies deployment.

**1. Prerequisites**

- A server with `Docker` and `docker-compose` installed.

**2. Configuration**

- Clone the project to your server.
- **Important**: Edit the `docker-compose.yaml` file and replace `your_strong_password_here` in the `NEO4J_AUTH` environment variable with your own strong password.
- Create a `.env` file and fill in your `GOOGLE_API_KEY` and the `NEO4J_PASSWORD` you just set in `docker-compose.yaml`. The passwords in both files must match perfectly.
  ```
  GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
  NEO4J_URI="neo4j://localhost:7687"
  NEO4J_USER="neo4j"
  NEO4J_PASSWORD="your_strong_password_here"
  ```

**3. Launch Services**

In the project root directory, execute the following command:

```bash
docker-compose up -d
```
This command will start the Neo4j database service in the background.

**4. Launch the App**

Next, in the same directory (after creating and activating the virtual environment as per the 'Installation & Running' section), launch the Streamlit app:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**5. Access**
- **Application UI**: `http://<YOUR_SERVER_IP>:8501`
- **Neo4j Browser**: `http://<YOUR_SERVER_IP>:7474` (You can view and query the stored graph data here)

### 📖 How to Use

1.  **Paste Text/Link**: Enter the text you want to analyze or a **YouTube video link** in the text area.
2.  **Or Upload File**: Click the upload button to select a local file in a supported format (e.g., PDF, DOCX).
3.  **Generate Graph**: Click the "生成图谱" button.
4.  **View Results**: Wait for the progress bar to complete. An interactive knowledge graph will be displayed. You can drag nodes, zoom, and hover to see detailed metadata.

### 🧪 How to Test

This project is configured with automated tests. After installing dependencies, you can run the tests from the project root:

```bash
pytest
```
