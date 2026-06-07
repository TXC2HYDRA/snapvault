from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


DEFAULT_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS file_chunks (
    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    offset INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    PRIMARY KEY (file_id, chunk_index)
);
"""


@dataclass
class Snapshot:
    id: int
    tag: Optional[str]
    created_at: str


class Catalog:
    """SQLite catalog for snapshots, files, and chunks."""

    def __init__(self, repo_path: Path) -> None:
        self.repo_path = Path(repo_path)
        self.db_path = self.repo_path / "metadata" / "catalog.sqlite"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(DEFAULT_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def create_snapshot(self, tag: Optional[str] = None) -> Snapshot:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO snapshots (tag) VALUES (?)", (tag,))
        self.conn.commit()
        sid = cur.lastrowid
        row = cur.execute("SELECT id, tag, created_at FROM snapshots WHERE id = ?", (sid,)).fetchone()
        return Snapshot(id=row["id"], tag=row["tag"], created_at=row["created_at"])

    def list_snapshots(self) -> List[Snapshot]:
        cur = self.conn.cursor()
        rows = cur.execute("SELECT id, tag, created_at FROM snapshots ORDER BY id DESC").fetchall()
        return [Snapshot(id=r["id"], tag=r["tag"], created_at=r["created_at"]) for r in rows]

    def add_file(self, snapshot_id: int, path: str, size: int) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO files (snapshot_id, path, size) VALUES (?, ?, ?)", (snapshot_id, path, size))
        self.conn.commit()
        return cur.lastrowid

    def add_chunk(self, chunk_id: str, size: int) -> None:
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO chunks (id, size) VALUES (?, ?)", (chunk_id, size))
        self.conn.commit()

    def link_file_chunk(self, file_id: int, chunk_id: str, offset: int, chunk_index: int) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO file_chunks (file_id, chunk_id, offset, chunk_index) VALUES (?, ?, ?, ?)",
            (file_id, chunk_id, offset, chunk_index),
        )
        self.conn.commit()

    def get_snapshot_files(self, snapshot_id: int) -> List[Tuple[int, str, int]]:
        cur = self.conn.cursor()
        rows = cur.execute("SELECT id, path, size FROM files WHERE snapshot_id = ?", (snapshot_id,)).fetchall()
        return [(r["id"], r["path"], r["size"]) for r in rows]

    def get_file_chunks(self, file_id: int) -> List[Tuple[int, str, int]]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT chunk_index, chunk_id, offset FROM file_chunks WHERE file_id = ? ORDER BY chunk_index",
            (file_id,),
        ).fetchall()
        return [(r["chunk_index"], r["chunk_id"], r["offset"]) for r in rows]

    def chunk_reference_count(self, chunk_id: str) -> int:
        cur = self.conn.cursor()
        row = cur.execute("SELECT COUNT(*) as c FROM file_chunks WHERE chunk_id = ?", (chunk_id,)).fetchone()
        return int(row[0])
