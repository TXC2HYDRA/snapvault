from __future__ import annotations

import abc
from pathlib import Path
from typing import Iterable


class StorageBackend(abc.ABC):
    """Abstract storage backend interface for storing and retrieving chunks."""

    @abc.abstractmethod
    def put_chunk(self, data: bytes) -> str:
        """Store a chunk and return its SHA-256 hex id."""

    @abc.abstractmethod
    def get_chunk(self, chunk_id: str) -> bytes:
        """Retrieve a chunk by its id. Raises KeyError if missing."""

    @abc.abstractmethod
    def has_chunk(self, chunk_id: str) -> bool:
        """Return True if the chunk exists in storage."""

    @abc.abstractmethod
    def delete_chunk(self, chunk_id: str) -> None:
        """Delete a chunk from storage if present."""

    @abc.abstractmethod
    def list_chunks(self) -> Iterable[str]:
        """List stored chunk ids."""


class LocalFilesystemBackend(StorageBackend):
    """Local filesystem backend that shards chunks by hash prefix.

    Chunks are stored under: <repo>/chunks/<first2hex>/<remaining_hex>
    """

    def __init__(self, repo_path: Path) -> None:
        self.repo_path = Path(repo_path)
        self.chunks_path = self.repo_path / "chunks"
        self.chunks_path.mkdir(parents=True, exist_ok=True)

    def _path_for(self, chunk_id: str) -> Path:
        prefix = chunk_id[:2]
        rest = chunk_id[2:]
        dir_path = self.chunks_path / prefix
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / rest

    def put_chunk(self, data: bytes) -> str:
        import hashlib

        chunk_id = hashlib.sha256(data).hexdigest()
        p = self._path_for(chunk_id)
        if not p.exists():
            # write atomically
            tmp = p.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(p)
        return chunk_id

    def get_chunk(self, chunk_id: str) -> bytes:
        p = self._path_for(chunk_id)
        if not p.exists():
            raise KeyError(chunk_id)
        return p.read_bytes()

    def has_chunk(self, chunk_id: str) -> bool:
        return self._path_for(chunk_id).exists()

    def delete_chunk(self, chunk_id: str) -> None:
        p = self._path_for(chunk_id)
        if p.exists():
            p.unlink()

    def list_chunks(self) -> Iterable[str]:
        for prefix_dir in sorted(self.chunks_path.iterdir()):
            if not prefix_dir.is_dir():
                continue
            prefix = prefix_dir.name
            for f in sorted(prefix_dir.iterdir()):
                yield prefix + f.name
