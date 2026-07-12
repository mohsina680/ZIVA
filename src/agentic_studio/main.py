from __future__ import annotations

from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from langchain_core.messages import HumanMessage, SystemMessage

from .config import get_settings, ensure_project_dirs
from .rag import build_vector_db, retrieve_context
from .graph import build_graph
from .llm import get_chat_model

app = typer.Typer(help="Local Qwen3 documentation, coding, and web-design agent")
console = Console()


@app.command()
def init() -> None:
    """Create the required folders."""
    settings = get_settings()
    ensure_project_dirs(settings)
    console.print("[green]Project folders are ready.[/green]")


@app.command()
def ingest() -> None:
    """Build/rebuild the local RAG vector database from data/docs/."""
    chunks = build_vector_db()
    console.print(f"[green]Vector DB created successfully with {chunks} chunks.[/green]")


@app.command()
def run(runbook: Path) -> None:
    """Run a Markdown instruction through the LangGraph agent."""
    settings = get_settings()
    ensure_project_dirs(settings)

    if not runbook.exists():
        raise typer.BadParameter(f"Runbook not found: {runbook}")

    runbook_text = runbook.read_text(encoding="utf-8")
    graph = build_graph()
    result = graph.invoke({"runbook_path": str(runbook), "runbook_text": runbook_text})

    console.rule("Agent Result")
    console.print(f"[bold]Task type:[/bold] {result.get('task_type')}")
    console.print("\n[bold]Generated output preview:[/bold]")
    console.print(str(result.get("generated_output", ""))[:2000])

    console.print("\n[bold]Review preview:[/bold]")
    console.print(str(result.get("review_output", ""))[:1200])

    saved_files = result.get("saved_files", [])
    if saved_files:
        table = Table(title="Saved Files")
        table.add_column("#")
        table.add_column("Path")
        for i, path in enumerate(saved_files, start=1):
            table.add_row(str(i), path)
        console.print(table)


@app.command()
def chat(message: str) -> None:
    """Ask Qwen3 a question with optional RAG context."""
    context = retrieve_context(message)
    llm = get_chat_model(temperature=0.2)
    response = llm.invoke([
        SystemMessage(content="You are a local assistant focused only on documentation, coding, and web design."),
        HumanMessage(content=f"RAG CONTEXT:\n{context}\n\nUSER MESSAGE:\n{message}"),
    ])
    console.print(response.content)


@app.command()
def status() -> None:
    """Show important configuration."""
    settings = get_settings()
    table = Table(title="Agent Configuration")
    table.add_column("Setting")
    table.add_column("Value")
    for key, value in settings.model_dump().items():
        table.add_row(key, str(value))
    console.print(table)


if __name__ == "__main__":
    app()
