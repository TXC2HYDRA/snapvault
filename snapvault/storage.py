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
