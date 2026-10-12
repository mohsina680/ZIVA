from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from .config import get_settings, ensure_project_dirs

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf", ".html", ".css", ".js", ".py"}


def _load_file(path: Path) -> List[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    if suffix in {".md", ".markdown"}:
        try:
            return UnstructuredMarkdownLoader(str(path)).load()
        except Exception:
            return TextLoader(str(path), encoding="utf-8").load()
    return TextLoader(str(path), encoding="utf-8").load()


def discover_documents(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]


def build_vector_db() -> int:
    settings = get_settings()
    ensure_project_dirs(settings)

    docs: List[Document] = []
    for file_path in discover_documents(settings.knowledge_dir):
        try:
            loaded = _load_file(file_path)
            for doc in loaded:
                doc.metadata["source"] = str(file_path)
            docs.extend(loaded)
        except Exception as exc:
            print(f"Skipped {file_path}: {exc}")

    if not docs:
        raise RuntimeError(f"No supported knowledge files found in {settings.knowledge_dir}")

    chunk_size = settings.rag_chunk_size
    chunk_overlap = min(settings.rag_chunk_overlap, max(0, chunk_size - 1))
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_total"] = total_chunks

    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(settings.vector_db_dir))
    return len(chunks)


def load_vector_db() -> FAISS | None:
    settings = get_settings()
    index_file = settings.vector_db_dir / "index.faiss"
    if not index_file.exists():
        return None
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    return FAISS.load_local(
        str(settings.vector_db_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve_context(query: str, k: Optional[int] = None, max_context_chars: Optional[int] = None) -> str:
    settings = get_settings()
    vectorstore = load_vector_db()
    if vectorstore is None:
        return ""
    limit_k = max(1, k or settings.rag_retrieval_k)
    context_limit = max_context_chars or settings.rag_max_context_chars
    docs = vectorstore.similarity_search(query, k=limit_k)
    blocks = []
    used_chars = 0
    for i, doc in enumerate(docs, start=1):
        if used_chars >= context_limit:
            break
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "?")
        chunk_total = doc.metadata.get("chunk_total", "?")
        content = doc.page_content.strip()
        header = f"[Context {i} | Source: {source} | Chunk {chunk_id}/{chunk_total}]"
        available_chars = max(0, context_limit - used_chars - len(header) - 2)
        if available_chars <= 0:
            break
        excerpt = content[:available_chars].strip()
        if not excerpt:
            continue
        block = f"{header}\n{excerpt}"
        blocks.append(block)
        used_chars += len(block) + 2
    return "\n\n".join(blocks)
