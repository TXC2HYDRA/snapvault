from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Generator, Tuple


def chunk_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> Generator[Tuple[int, bytes, str], None, None]:
    """Yield file chunks with SHA-256 hash metadata.

    Args:
        path: Path to the file to chunk.
        chunk_size: Maximum size of each chunk in bytes.

    Yields:
        Tuples of (offset, chunk_bytes, sha256_hex).
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    offset = 0
    with Path(path).open("rb") as file_handle:
        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break
            digest = hashlib.sha256(chunk).hexdigest()
            yield offset, chunk, digest
            offset += len(chunk)
