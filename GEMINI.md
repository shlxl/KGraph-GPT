# GEMINI.md - KGraph-GPT

## Project Overview

This repository contains the `Streamlit-KG-Extractor` project, a Python web application designed to extract knowledge graphs from text and visualize them interactively. 

The application is built with Streamlit and uses Google's Gemini 2.5 Pro model via the Langchain framework to perform the core Natural Language Processing task. It identifies entities and their relationships in a given text and then uses the Pyvis library to render the resulting graph in an interactive HTML component.

The architecture is straightforward: a single-file application (`app.py`) handles the UI, user input (text area or file upload), backend logic for calling the LLM, and visualization rendering.

## Building and Running

### 1. Dependencies

Install the necessary Python packages from `requirements.txt`:

```bash
pip install -r Streamlit-KG-Extractor/requirements.txt
```

### 2. Configuration

The application requires a Google API key. You must create a `.env` file inside the `Streamlit-KG-Extractor` directory with your key:

```
# In Streamlit-KG-Extractor/.env
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

### 3. Running the Application

To run the web application, navigate to the project directory and use the `streamlit` command:

```bash
cd Streamlit-KG-Extractor
streamlit run app.py
```

## Development Conventions

- **Main Logic**: All application code is contained within `app.py`.
- **Dependencies**: Project dependencies are managed in `requirements.txt`.
- **Configuration**: API keys and other secrets are loaded from a `.env` file using `python-dotenv`.
- **Testing**: There are currently no automated tests in the project. Future development could involve adding tests for the graph generation logic.
