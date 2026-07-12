# Local Documentation, Coding, and Web Design and Data Extraction Agent

This is a clean local agentic AI project focused only on:

1. Documentation generation
2. Coding and web development
3. Web design and UI/UX planning
4. Data Extraction

It uses:

- Qwen3 4B Thinking quantized through Ollama or LM Studio
- LangGraph for workflow routing
- LangChain for LLM, RAG, and tool integration
- FAISS vector database for local RAG
- Markdown runbooks for task instructions
- Local workspace output

No VM automation, no Docker Swarm, no SSH, and no infrastructure execution are included.

## Folder Meaning

```text
runbooks/      = Markdown instructions for tasks you want to run now
data/docs/     = knowledge/reference material for RAG
workspace/     = generated docs, code, and design outputs
storage/       = FAISS vector database
logs/          = future logs/reports
src/           = Python agent source code
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```

## Ollama Setup

Install Ollama, then run:

```bash
ollama pull qwen3:4b-thinking
ollama serve
```

Check `.env`:

```env
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_API_KEY=ollama
TEXT_MODEL=qwen3:4b-thinking
```

## LM Studio Setup

Load a Qwen3 4B Thinking GGUF quantized model in LM Studio and start the local server.

Then set `.env`:

```env
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_API_KEY=lm-studio
TEXT_MODEL=your-loaded-model-name
```

## Build RAG

Put your reference files in `data/docs/`, then run:

```bash
python -m src.agentic_studio ingest
```

## Run a Task

Documentation:

```bash
python -m src.agentic_studio run runbooks/documentation/create_project_report.md
```

Coding:

```bash
python -m src.agentic_studio run runbooks/coding/create_landing_page.md
```

Design:

```bash
python -m src.agentic_studio run runbooks/design/create_clinic_ui_design.md
```

Outputs are saved in `workspace/`.

## Test the Project Code

```bash
PYTHONPATH=. pytest -q
```

## Check Local Model Connection

```bash
python scripts/check_local_model.py
```

Expected output should contain something like:

```text
model-ok
```
