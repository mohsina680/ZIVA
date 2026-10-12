from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

from src.agentic_studio.config import get_settings, ensure_project_dirs
from src.agentic_studio.graph import build_graph
from src.agentic_studio.llm import get_chat_model
from src.agentic_studio.prompts import build_agent_user_message
from src.agentic_studio.rag import build_vector_db, retrieve_context


TASK_TYPE_TO_FOLDER = {
    "Documentation": "documentation",
    "Coding": "coding",
    "Web Design": "design",
    "Document Extraction": "document_extraction",
}


def _list_runbooks(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*.md") if p.is_file()])


def _make_runbook_text(goal: str, requirements: str, output_required: str, style: str) -> str:
    lines = [
        "# Task",
        "",
        "## Goal",
        goal.strip(),
        "",
        "## Requirements",
        requirements.strip(),
        "",
        "## Output Required",
        output_required.strip(),
        "",
        "## Style",
        style.strip(),
        "",
    ]
    return "\n".join(lines)


def _run_graph(runbook_path: str, runbook_text: str) -> dict:
    graph = build_graph()
    return graph.invoke({"runbook_path": runbook_path, "runbook_text": runbook_text})


def main() -> None:
    settings = get_settings()
    ensure_project_dirs(settings)

    st.set_page_config(page_title="ZIVA Agentic Studio", page_icon="🧠", layout="wide")
    st.title("🧠 ZIVA Agentic Studio")
    st.caption("Interactive app for documentation, coding, web design, and document extraction workflows.")

    tabs = st.tabs([
        "Run Existing Runbook",
        "Create & Run Task",
        "Knowledge Base",
        "Agent Chat",
        "System Status",
    ])

    with tabs[0]:
        st.subheader("Run Existing Runbook")
        runbooks = _list_runbooks(settings.runbook_dir)
        if not runbooks:
            st.info("No runbook files found. Create one in runbooks/ or use the Create & Run Task tab.")
        else:
            selected = st.selectbox(
                "Select a runbook",
                options=runbooks,
                format_func=lambda p: str(p),
            )
            text = selected.read_text(encoding="utf-8")
            st.text_area("Runbook preview", value=text, height=280, disabled=True)

            if st.button("Run selected runbook", type="primary"):
                with st.spinner("Running graph workflow..."):
                    result = _run_graph(str(selected), text)
                st.success("Run complete.")
                st.write(f"**Task type:** `{result.get('task_type', 'unknown')}`")
                st.text_area("Generated output", value=str(result.get("generated_output", "")), height=260)
                st.text_area("Review output", value=str(result.get("review_output", "")), height=200)
                st.json({"saved_files": result.get("saved_files", [])})

    with tabs[1]:
        st.subheader("Create and Run a Task")
        task_label = st.selectbox("Workflow type", list(TASK_TYPE_TO_FOLDER.keys()))
        goal = st.text_input("Goal", placeholder="Describe the exact objective")
        requirements = st.text_area("Requirements", placeholder="- Requirement 1\n- Requirement 2", height=160)
        output_required = st.text_area("Output Required", placeholder="- Files\n- Format\n- Deliverables", height=140)
        style = st.text_input("Style", value="Clean, modern, production-ready.")

        runbook_text = _make_runbook_text(goal, requirements, output_required, style)
        st.text_area("Generated runbook", value=runbook_text, height=260)

        if st.button("Run generated task", type="primary"):
            folder = TASK_TYPE_TO_FOLDER[task_label]
            pseudo_path = f"runbooks/{folder}/ui_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with st.spinner("Running graph workflow..."):
                result = _run_graph(pseudo_path, runbook_text)
            st.success("Run complete.")
            st.write(f"**Task type:** `{result.get('task_type', 'unknown')}`")
            st.text_area("Generated output", value=str(result.get("generated_output", "")), height=260)
            st.text_area("Review output", value=str(result.get("review_output", "")), height=200)
            st.json({"saved_files": result.get("saved_files", [])})

    with tabs[2]:
        st.subheader("Knowledge Base / RAG")
        st.write(f"Knowledge directory: `{settings.knowledge_dir}`")
        st.write(f"Vector DB directory: `{settings.vector_db_dir}`")
        st.caption("Place reference files under data/docs/ and rebuild embeddings.")

        if st.button("Rebuild vector database", type="primary"):
            with st.spinner("Building vector database..."):
                chunks = build_vector_db()
            st.success(f"Vector DB rebuilt successfully with {chunks} chunks.")

    with tabs[3]:
        st.subheader("Agent Chat")
        message = st.text_area("Message", placeholder="Ask about code, docs, design, or extraction tasks", height=120)
        if st.button("Send", type="primary"):
            with st.spinner("Retrieving context and generating response..."):
                context = retrieve_context(message)
                llm = get_chat_model(temperature=0.2)
                response = llm.invoke([
                    SystemMessage(content="You are a local assistant focused on documentation, coding, web design, and document extraction."),
                    HumanMessage(content=build_agent_user_message("USER MESSAGE", message, context)),
                ])
            st.text_area("Response", value=str(response.content), height=260)

    with tabs[4]:
        st.subheader("System Status")
        st.json(json.loads(settings.model_dump_json()))

        runbooks = _list_runbooks(settings.runbook_dir)
        st.write(f"Runbooks found: **{len(runbooks)}**")

        workspace = settings.workspace_dir
        if workspace.exists():
            recent = sorted([p for p in workspace.rglob("*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)[:20]
            st.write("Recent workspace files:")
            for path in recent:
                st.code(str(path))
        else:
            st.info("Workspace directory does not exist yet.")


if __name__ == "__main__":
    main()
