from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os


class Settings(BaseModel):
    local_llm_base_url: str = "http://localhost:11434/v1"
    local_llm_api_key: str = "ollama"
    text_model: str = "qwen3:4b-thinking"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    runbook_dir: Path = Path("runbooks")
    knowledge_dir: Path = Path("data/docs")
    workspace_dir: Path = Path("workspace")
    log_dir: Path = Path("logs")
    vector_db_dir: Path = Path("storage/faiss_index")

    task_scope: str = "documentation,coding,web_design"
    save_raw_model_output: bool = True
    extract_file_blocks: bool = True


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        local_llm_base_url=os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1"),
        local_llm_api_key=os.getenv("LOCAL_LLM_API_KEY", "ollama"),
        text_model=os.getenv("TEXT_MODEL", "qwen3:4b-thinking"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        runbook_dir=Path(os.getenv("RUNBOOK_DIR", "runbooks")),
        knowledge_dir=Path(os.getenv("KNOWLEDGE_DIR", "data/docs")),
        workspace_dir=Path(os.getenv("WORKSPACE_DIR", "workspace")),
        log_dir=Path(os.getenv("LOG_DIR", "logs")),
        vector_db_dir=Path(os.getenv("VECTOR_DB_DIR", "storage/faiss_index")),
        task_scope=os.getenv("TASK_SCOPE", "documentation,coding,web_design"),
        save_raw_model_output=os.getenv("SAVE_RAW_MODEL_OUTPUT", "true").lower() == "true",
        extract_file_blocks=os.getenv("EXTRACT_FILE_BLOCKS", "true").lower() == "true",
    )


def ensure_project_dirs(settings: Settings) -> None:
    for path in [
        settings.runbook_dir,
        settings.knowledge_dir,
        settings.workspace_dir,
        settings.log_dir,
        settings.vector_db_dir.parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)
