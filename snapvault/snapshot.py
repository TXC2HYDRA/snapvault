from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .chunker import chunk_file
from .storage import LocalFilesystemBackend
from .catalog import Catalog


def backup(source: Path, repo_path: Path, tag: str | None = None) -> int:
    """Create a snapshot of `source` in `repo_path`. Returns snapshot id.

    This function walks `source`, chunks files using `chunk_file`, stores
    chunks using `LocalFilesystemBackend`, and records metadata in `Catalog`.
    """
    source = Path(source)
    repo_path = Path(repo_path)

    backend = LocalFilesystemBackend(repo_path)
    catalog = Catalog(repo_path)

    snap = catalog.create_snapshot(tag=tag)

    for p in source.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(source).as_posix()
        size = p.stat().st_size
        file_id = catalog.add_file(snap.id, rel, size)

        chunk_index = 0
        for offset, chunk_bytes, chunk_id in chunk_file(p):
            if not backend.has_chunk(chunk_id):
                backend.put_chunk(chunk_bytes)
                catalog.add_chunk(chunk_id, len(chunk_bytes))
            catalog.link_file_chunk(file_id, chunk_id, offset, chunk_index)
            chunk_index += 1

    catalog.close()
    return snap.id


def restore(snapshot_id: int, target: Path, repo_path: Path) -> None:
    """Restore snapshot `snapshot_id` from `repo_path` into `target` directory."""
    repo_path = Path(repo_path)
    target = Path(target)

    backend = LocalFilesystemBackend(repo_path)
    catalog = Catalog(repo_path)

    files = catalog.get_snapshot_files(snapshot_id)
    for file_id, rel_path, size in files:
        out_path = target / Path(rel_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as fh:
            chunks = catalog.get_file_chunks(file_id)
            for _, chunk_id, _ in chunks:
                chunk_bytes = backend.get_chunk(chunk_id)
                fh.write(chunk_bytes)

    catalog.close()
