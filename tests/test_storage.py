from pathlib import Path

import hashlib

from snapvault.storage import LocalFilesystemBackend


def test_storage_roundtrip_and_idempotency(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    backend = LocalFilesystemBackend(repo)

    data = b"hello world"
    cid = backend.put_chunk(data)

    assert backend.has_chunk(cid)
    assert backend.get_chunk(cid) == data

    # idempotent put
    cid2 = backend.put_chunk(data)
    assert cid2 == cid

    listed = list(backend.list_chunks())
    assert cid in listed

    backend.delete_chunk(cid)
    assert not backend.has_chunk(cid)
    assert list(backend.list_chunks()) == []
