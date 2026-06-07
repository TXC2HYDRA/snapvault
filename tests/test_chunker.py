import hashlib
from pathlib import Path

from snapvault.chunker import chunk_file


def test_chunk_file_small_file(tmp_path: Path) -> None:
    content = b"hello snapvault"
    file_path = tmp_path / "small.bin"
    file_path.write_bytes(content)

    chunks = list(chunk_file(file_path, chunk_size=1024))

    assert len(chunks) == 1
    offset, chunk_bytes, sha = chunks[0]
    assert offset == 0
    assert chunk_bytes == content
    assert sha == hashlib.sha256(content).hexdigest()


def test_chunk_file_exact_multiple(tmp_path: Path) -> None:
    chunk_size = 8
    data = b"abcdefgh" * 3
    file_path = tmp_path / "exact.bin"
    file_path.write_bytes(data)

    chunks = list(chunk_file(file_path, chunk_size=chunk_size))

    assert len(chunks) == 3
    assert [offset for offset, _, _ in chunks] == [0, 8, 16]
    assert b"".join(chunk for _, chunk, _ in chunks) == data
    assert chunks[0][2] == hashlib.sha256(data[:8]).hexdigest()


def test_chunk_file_empty_file(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.bin"
    file_path.write_bytes(b"")

    chunks = list(chunk_file(file_path, chunk_size=1024))

    assert chunks == []


def test_chunk_file_large_file_streams(tmp_path: Path) -> None:
    chunk_size = 1024
    data = b"x" * (chunk_size * 2 + 100)
    file_path = tmp_path / "large.bin"
    file_path.write_bytes(data)

    chunks = list(chunk_file(file_path, chunk_size=chunk_size))

    assert len(chunks) == 3
    assert [len(chunk) for _, chunk, _ in chunks] == [chunk_size, chunk_size, 100]
    assert b"".join(chunk for _, chunk, _ in chunks) == data
    assert chunks[-1][0] == chunk_size * 2
