from __future__ import annotations

from langgraph.graph import StateGraph, END

from .state import AgentState
from .router import classify_task
from .rag import retrieve_context
from .agents.documentation_agent import run_documentation_agent
from .agents.coding_agent import run_coding_agent
from .agents.design_agent import run_design_agent
from .agents.document_agent import run_document_agent
from .agents.review_agent import run_review_agent
from .tools.files import save_agent_output, save_extracted_files
from .config import get_settings


def retrieve_node(state: AgentState) -> AgentState:
    query = f"{state.get('runbook_path', '')}\n{state.get('runbook_text', '')}"
    return {"rag_context": retrieve_context(query)}


def route_node(state: AgentState) -> AgentState:
    task_type = classify_task(state.get("runbook_text", ""), state.get("runbook_path", ""))
    return {"task_type": task_type}


def documentation_node(state: AgentState) -> AgentState:
    output = run_documentation_agent(state["runbook_text"], state.get("rag_context", ""))
    return {"generated_output": output}


def coding_node(state: AgentState) -> AgentState:
    output = run_coding_agent(state["runbook_text"], state.get("rag_context", ""))
    return {"generated_output": output}


def design_node(state: AgentState) -> AgentState:
    output = run_design_agent(state["runbook_text"], state.get("rag_context", ""))
    return {"generated_output": output}


def document_extraction_node(state: AgentState) -> AgentState:
    output = run_document_agent(state["runbook_text"], state.get("rag_context", ""))
    return {"generated_output": output}


def unknown_node(state: AgentState) -> AgentState:
    output = (
        "The task type could not be classified. Please use one of these folders:\n"
        "- runbooks/documentation/\n"
        "- runbooks/coding/\n"
        "- runbooks/design/\n"
        "- runbooks/document_extraction/\n"
    )
    return {"generated_output": output, "errors": ["Unknown task type"]}


def review_node(state: AgentState) -> AgentState:
    if state.get("task_type") == "unknown":
        return {"review_output": "Review skipped because task type is unknown."}
    review = run_review_agent(state["runbook_text"], state.get("generated_output", ""))
    return {"review_output": review}


def save_node(state: AgentState) -> AgentState:
    settings = get_settings()
    task_type = state.get("task_type", "unknown")
    output = state.get("generated_output", "")
    review = state.get("review_output", "")
    saved = save_agent_output(task_type, output, review)
    if settings.extract_file_blocks:
        saved.extend(save_extracted_files(task_type, output))
    return {"saved_files": saved}


def _route_condition(state: AgentState) -> str:
    return state.get("task_type", "unknown")


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve_context", retrieve_node)
    graph.add_node("route", route_node)
    graph.add_node("documentation", documentation_node)
    graph.add_node("coding", coding_node)
    graph.add_node("web_design", design_node)
    graph.add_node("document_extraction", document_extraction_node)
    graph.add_node("unknown", unknown_node)
    graph.add_node("review", review_node)
    graph.add_node("save", save_node)

    graph.set_entry_point("retrieve_context")
    graph.add_edge("retrieve_context", "route")
    graph.add_conditional_edges(
        "route",
        _route_condition,
        {
            "documentation": "documentation",
            "coding": "coding",
            "web_design": "web_design",
            "document_extraction": "document_extraction",
            "unknown": "unknown",
        },
    )
    graph.add_edge("documentation", "review")
    graph.add_edge("coding", "review")
    graph.add_edge("web_design", "review")
    graph.add_edge("document_extraction", "review")
    graph.add_edge("unknown", "review")
    graph.add_edge("review", "save")
    graph.add_edge("save", END)

    return graph.compile()