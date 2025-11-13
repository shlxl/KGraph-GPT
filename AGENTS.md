# Repository Guidelines

## Project Structure & Module Organization
`app.py` is the Streamlit UI that orchestrates document ingestion, LangChain/Gemini calls, and Neo4j exports. Parser utilities stay in `src/parsers/` (e.g., `MarkdownMultiDocumentParser`). Sample corpora, REL_SET JSON, and the prompt template live at the repo root alongside deployment artifacts like `docker-compose.yaml` and `requirements.txt`. UI vendor bundles remain in `lib/`, and executable scenarios/tests live in `tests/`. Keep `.env` (keys, Neo4j creds) at the root but out of version control.

## Build, Test, and Development Commands
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
docker-compose up -d
pytest
pytest -k scenario
```
Line 1-2 set up the virtualenv and install Python deps. `streamlit run app.py` launches the UI (add `--server.port 8501 --server.address 0.0.0.0` for remote hosts). `docker-compose up -d` starts Neo4j when you need persistence. Use `pytest` for the full suite or `pytest -k scenario` for targeted GraphRAG workflows. Ensure `.env` exposes `GOOGLE_API_KEY`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` before running.

## Coding Style & Naming Conventions
Adhere to PEP 8 with four-space indentation and retain existing type hints. Functions, modules, and Streamlit state keys use `snake_case`; classes, Pydantic models, and parsers use `PascalCase`. Keep configuration constants upper-case and colocated near the top of `app.py`. Write bilingual UI strings only when updating existing bilingual sections, and prefer descriptive variable names over abbreviations in graph extraction logic.

## Testing Guidelines
Pytest plus `pytest-mock` cover both unit and integration flows (`tests/test_app.py`, `tests/test_graphrag_scenarios.py`). Integration tests that call Gemini are wrapped in `@pytest.mark.skipif` for missing `GOOGLE_API_KEY`; respect that pattern when adding long-running cases. Name tests `test_<feature>_<behavior>`, assert on explicit node/relationship shapes, and mock LangChain boundaries so fast tests guard prompt formatting regressions.

## Commit & Pull Request Guidelines
History shows Conventional Commit prefixes (`feat:`, `docs:`, `fix:`) followed by concise present-tense summaries—continue that practice, even for multilingual commits. Each PR should explain the motivation, list verification steps (`pytest`, manual Streamlit checks), mention touched corpora/REL_SET files, and attach screenshots or GIFs for UI-facing changes. Link issues or roadmap items whenever possible.

## Security & Configuration Tips
Keep secrets in `.env`; never commit API keys, corpora with private data, or generated exports. When editing `docker-compose.yaml`, rotate `NEO4J_AUTH` and mirror the value inside `.env`. Validate any new REL_SET schema additions and document the expected directory layout (`GraphRAG-Extract-Best-Example-CoralWind-zh/corpus/`) so other contributors can reproduce your runs.
