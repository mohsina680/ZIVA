"""
Document extraction cache using file hash.
"""
from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta

from .extractors.base import ExtractionResult


class ExtractionCache:
    """
    Cache for document extraction results.

    Uses file hash (xxhash) to quickly identify cached documents.
    Stores results as JSON files in a cache directory.
    """

    def __init__(
        self,
        cache_dir: str = "storage/document_cache",
        ttl_hours: int = 72
    ):
        """
        Initialize the extraction cache.

        Args:
            cache_dir: Directory to store cached results
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

        # In-memory index for fast lookups
        self._index: Dict[str, dict] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load cache index from disk."""
        index_file = self.cache_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self._index = json.load(f)
            except Exception:
                self._index = {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        index_file = self.cache_dir / "index.json"
        try:
            with open(index_file, 'w') as f:
                json.dump(self._index, f, indent=2)
        except Exception:
            pass

    def _compute_hash(self, file_path: str) -> str:
        """
        Compute hash of a file for cache key.

        Uses MD5 for speed (file integrity check, not security).
        """
        path = Path(file_path)
        if not path.exists():
            return hashlib.md5(file_path.encode()).hexdigest()

        # Use file mtime and size for quick comparison
        stat = path.stat()
        quick_hash = f"{path.name}_{stat.st_size}_{stat.st_mtime}"

        # Full content hash for larger files
        if stat.st_size > 10 * 1024 * 1024:  # > 10MB
            hasher = hashlib.md5()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()

        return hashlib.md5(quick_hash.encode()).hexdigest()

    def get(self, file_path: str) -> Optional[ExtractionResult]:
        """
        Get cached extraction result for a file.

        Args:
            file_path: Path to the document

        Returns:
            Cached ExtractionResult or None if not found/stale
        """
        file_hash = self._compute_hash(file_path)

        if file_hash not in self._index:
            return None

        entry = self._index[file_hash]

        # Check if cache is stale
        cached_time = entry.get("cached_at", 0)
        if time.time() - cached_time > self.ttl_seconds:
            # Remove stale entry
            del self._index[file_hash]
            self._save_index()
            return None

        # Load cached result
        cache_file = self.cache_dir / f"{file_hash}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            return ExtractionResult(
                text=data.get("text", ""),
                confidence=data.get("confidence", 0),
                extractor_name=data.get("extractor_name", "unknown"),
                page_count=data.get("page_count", 1),
                language=data.get("language", "unknown"),
                extraction_time_ms=data.get("extraction_time_ms", 0),
                cache_hit=True,
                error=data.get("error")
            )
        except Exception:
            return None

    def set(self, file_path: str, result: ExtractionResult) -> None:
        """
        Cache an extraction result.

        Args:
            file_path: Path to the source document
            result: ExtractionResult to cache
        """
        file_hash = self._compute_hash(file_path)

        # Save result data
        cache_file = self.cache_dir / f"{file_hash}.json"
        cache_data = {
            "text": result.text,
            "confidence": result.confidence,
            "extractor_name": result.extractor_name,
            "page_count": result.page_count,
            "language": result.language,
            "extraction_time_ms": result.extraction_time_ms,
            "error": result.error,
            "file_path": str(Path(file_path).resolve()),
            "cached_at": time.time()
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            # Update index
            self._index[file_hash] = {
                "cached_at": cache_data["cached_at"],
                "file_path": str(Path(file_path).resolve()),
                "extractor": result.extractor_name,
                "confidence": result.confidence
            }
            self._save_index()
        except Exception:
            pass

    def invalidate(self, file_path: str) -> bool:
        """
        Invalidate cache entry for a file.

        Args:
            file_path: Path to the document

        Returns:
            True if entry was found and removed
        """
        file_hash = self._compute_hash(file_path)

        if file_hash not in self._index:
            return False

        # Remove cache file
        cache_file = self.cache_dir / f"{file_hash}.json"
        if cache_file.exists():
            cache_file.unlink()

        # Remove from index
        del self._index[file_hash]
        self._save_index()

        return True

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = 0
        for file_hash in list(self._index.keys()):
            cache_file = self.cache_dir / f"{file_hash}.json"
            if cache_file.exists():
                cache_file.unlink()
            count += 1

        self._index = {}
        self._save_index()
        return count

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_size = sum(
            (self.cache_dir / f).stat().st_size
            for f in self.cache_dir.iterdir()
            if f.is_file() and f.name != "index.json"
        )

        return {
            "entries": len(self._index),
            "total_size_bytes": total_size,
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl_seconds / 3600
        }


# Default cache instance
_default_cache: Optional[ExtractionCache] = None


def get_default_cache() -> ExtractionCache:
    """Get or create the default cache instance."""
    global _default_cache
    if _default_cache is None:
        _default_cache = ExtractionCache()
    return _default_cache