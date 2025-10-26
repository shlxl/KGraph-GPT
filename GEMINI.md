# GEMINI.md - KGraph-GPT Project

## Project Overview

This repository contains a Python web application built with Streamlit. Its primary purpose is to extract knowledge graphs from various unstructured text sources and visualize them as interactive, colored, and directed graphs.

The application leverages Google's Gemini 2.5 Pro model through the LangChain framework to perform the core Natural Language Processing tasks, including entity extraction, relationship identification, and property discovery. The final graph is rendered using the Pyvis library.

The architecture is centered around a single-file application (`app.py`) which handles the UI, input logic, and visualization. The core graph generation logic is separated into testable functions. The project also includes a suite of automated tests using `pytest`.

### Key Features
- **Multi-Source Input**: Accepts plain text, YouTube video links (for transcript extraction), and various file formats (`.txt`, `.pdf`, `.docx`, `.odt`, `.html`, `.md`).
- **Advanced Graph Extraction**: Identifies nodes, properties, and both uni-directional and bi-directional relationships.
- **Rich Interactive Visualization**: Displays graphs with colored nodes/edges, directionality arrows, and detailed metadata in tooltips on hover.

## Building and Running

### 1. Dependencies

All project dependencies are listed in `requirements.txt`. To install them, first create and activate a virtual environment, then run:

```bash
pip install -r requirements.txt
```

### 2. Configuration

The application requires a Google API key to access the Gemini model. You must create a `.env` file in the project root with your key:

```
# In .env
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

### 3. Running the Application

To run the web application, execute the following command in the project root:

```bash
streamlit run app.py
```

### 4. Running Tests

The project includes both integration and unit tests. To run the test suite, execute:

```bash
pytest
```

## Development Conventions

- **Main Logic**: The primary application logic and UI are contained within `app.py`.
- **Dependencies**: All Python package dependencies are managed in `requirements.txt`.
- **Configuration**: API keys and other secrets are loaded from a `.env` file.
- **Testing**: Automated tests are located in the `tests/` directory and are run using the `pytest` framework. The test suite includes:
    - An integration test that makes a real API call to verify end-to-end functionality.
    - A unit test that uses `pytest-mock` to test logic without network access.
- **Documentation**: The `README.md` file serves as the single source of truth for user-facing and general project documentation.
