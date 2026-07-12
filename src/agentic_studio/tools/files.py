from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from ..config import get_settings

FILE_BLOCK_PATTERN = re.compile(
    r"```file\s+path=(?P<path>[^\n]+)\n(?P<content>.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)


def _safe_workspace_path(relative_path: str) -> Path:
    settings = get_settings()
    workspace_root = settings.workspace_dir.resolve()
    target = (workspace_root / relative_path).resolve()
    if not str(target).startswith(str(workspace_root)):
        raise ValueError(f"Unsafe output path outside workspace: {relative_path}")
    return target


def save_text(relative_path: str, content: str) -> str:
    target = _safe_workspace_path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


def save_agent_output(task_type: str, output: str, review: str = "") -> List[str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = f"{task_type}/{timestamp}"
    saved = [save_text(f"{base_dir}/agent_output.md", output)]
    if review:
        saved.append(save_text(f"{base_dir}/review.md", review))
    return saved


def extract_file_blocks(output: str) -> List[Tuple[str, str]]:
    files: List[Tuple[str, str]] = []
    for match in FILE_BLOCK_PATTERN.finditer(output):
        path = match.group("path").strip().strip('"').strip("'")
        content = match.group("content")
        files.append((path, content))
    return files


def save_extracted_files(task_type: str, output: str) -> List[str]:
    saved: List[str] = []
    blocks = extract_file_blocks(output)
    for relative_path, content in blocks:
        # Force generated files under a task namespace even if the model provides a bare path.
        relative_path = relative_path.replace("\\", "/").lstrip("/")
        if relative_path.startswith("workspace/"):
            relative_path = relative_path[len("workspace/"):]
        saved.append(save_text(f"{task_type}/generated_files/{relative_path}", content))
    return saved
