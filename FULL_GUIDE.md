# Full From-Scratch Guide: Local Qwen3 Documentation, Coding, and Web Design Agent

## 1. Final Scope

This project is a local AI agent for:

- Documentation writing
- Coding and web development
- Web UI/UX design planning

It intentionally does not include:

- VM automation
- Docker Swarm
- SSH execution
- Server operations
- Infrastructure automation

## 2. Final Architecture

```text
User Markdown Runbook
        ↓
LangGraph workflow
        ↓
RAG context retrieval
        ↓
Task router
        ├── Documentation Agent
        ├── Coding Agent
        └── Web Design Agent
        ↓
Review Agent
        ↓
Save generated output in workspace/
```

## 3. Why Each Component Exists

### Qwen3 4B Thinking

Used as the local reasoning and generation model.

### LangGraph

Used to control the workflow. It decides the route and moves state from one node to another.

### LangChain

Used to connect the local LLM, embeddings, retriever, and vector database.

### RAG

Used so your agent can reference your own writing style, coding rules, templates, and project requirements.

### FAISS Vector DB

Used locally to store searchable embeddings of documents inside `data/docs/`.

## 4. Storage Requirements

Approximate storage:

| Item | Estimated Size |
|---|---:|
| Python virtual environment | 1.5 GB - 3 GB |
| Python packages + dependencies | 1 GB - 2 GB |
| Sentence-transformer embedding model | 100 MB - 500 MB |
| FAISS vector index for small docs | 10 MB - 500 MB |
| Qwen3 4B Thinking Q4 model | 2.5 GB - 4 GB |
| Qwen3 4B Thinking Q5/Q6 model | 4 GB - 6 GB |
| Workspace generated files | depends on usage |

Minimum free storage:

```text
10 GB free
```

Recommended free storage:

```text
20 GB - 30 GB free
```

If you use LM Studio and download multiple GGUF models, keep:

```text
40 GB+ free
```

## 5. RAM Requirements

| Setup | RAM |
|---|---:|
| Qwen3 4B Q4 + small RAG | 12 GB minimum |
| Comfortable local use | 16 GB |
| Better multitasking | 32 GB |

Your Core i7 11th Gen laptop is fine if it has at least 16 GB RAM. 32 GB is better.

## 6. Install Steps

### Step 1: Install Python

Use Python 3.11 or 3.12.

Check:

```bash
python --version
```

### Step 2: Install Ollama or LM Studio

Recommended first option: Ollama.

```bash
ollama pull qwen3:4b-thinking
ollama serve
```

Alternative: LM Studio with a Qwen3 4B Thinking GGUF Q4 model.

### Step 3: Create Python Environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Create Environment File

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
copy .env.example .env
```

### Step 6: Add RAG Knowledge

Place reusable knowledge files in:

```text
data/docs/
```

Examples:

```text
data/docs/writing_style.md
data/docs/coding_rules.md
data/docs/web_design_rules.md
```

### Step 7: Build Vector DB

```bash
python -m src.agentic_studio ingest
```

### Step 8: Run a Documentation Task

```bash
python -m src.agentic_studio run runbooks/documentation/create_project_report.md
```

### Step 9: Run a Coding Task

```bash
python -m src.agentic_studio run runbooks/coding/create_landing_page.md
```

### Step 10: Run a Web Design Task

```bash
python -m src.agentic_studio run runbooks/design/create_clinic_ui_design.md
```

## 7. How to Write Your Own Markdown Runbook

Create a file like:

```text
runbooks/coding/create_portfolio_website.md
```

Example:

```markdown
# Task: Create Portfolio Website

## Goal
Create a modern personal portfolio website.

## Requirements
- Hero section
- About section
- Projects section
- Skills section
- Contact section
- Responsive layout

## Output Required
- index.html
- style.css
- script.js

## Style
Modern, clean, dark theme with blue accent.
```

Then run:

```bash
python -m src.agentic_studio run runbooks/coding/create_portfolio_website.md
```

## 8. File Block Format

For automatic file saving, the model is instructed to output files like this:

```text
```file path=my_project/index.html
<html>...</html>
```
```

The agent extracts those blocks and saves them under:

```text
workspace/coding/generated_files/
```

## 9. Recommended Model Settings

Ollama `.env`:

```env
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_API_KEY=ollama
TEXT_MODEL=qwen3:4b-thinking
```

LM Studio `.env`:

```env
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_API_KEY=lm-studio
TEXT_MODEL=your-loaded-qwen3-4b-thinking-model-name
```

## 10. Practical Usage Pattern

Use this pattern every time:

1. Put project rules/templates in `data/docs/`.
2. Run `python -m src.agentic_studio ingest`.
3. Create a task Markdown file in `runbooks/`.
4. Run the task.
5. Check generated files in `workspace/`.
6. Improve your runbook if output is not specific enough.

## 11. Best Prompting Style for Runbooks

Good runbooks include:

- Clear goal
- Output files required
- Style requirements
- Technology stack
- Sections/pages/components
- Constraints
- Folder/output preference

Bad runbooks are vague, such as:

```text
make website good
```

Better:

```text
Create a responsive clinic landing page with hero, services, doctors, appointment CTA, and footer. Use white background, blue-green accents, rounded cards, and clean CSS. Generate index.html, style.css, script.js.
```

## 12. End Result

After setup, your local laptop becomes a focused agentic workspace for:

- Writing documents
- Creating project reports
- Building web pages
- Designing UI layouts
- Generating frontend code
- Reviewing its own output
- Using your own reference knowledge through RAG
