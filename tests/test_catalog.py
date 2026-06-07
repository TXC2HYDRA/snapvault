from pathlib import Path

from snapvault.catalog import Catalog


def test_catalog_crud_and_reference_counting(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    cat = Catalog(repo)

    snap = cat.create_snapshot(tag="first")
    assert snap.tag == "first"

    file_id = cat.add_file(snap.id, "foo.txt", 123)
    assert file_id > 0

    # add two chunks and link them
    cat.add_chunk("a" * 64, 100)
    cat.add_chunk("b" * 64, 200)
    cat.link_file_chunk(file_id, "a" * 64, 0, 0)
    cat.link_file_chunk(file_id, "b" * 64, 100, 1)

    files = cat.get_snapshot_files(snap.id)
    assert len(files) == 1
    assert files[0][1] == "foo.txt"

    chunks = cat.get_file_chunks(file_id)
    assert chunks[0][1] == "a" * 64
    assert chunks[1][1] == "b" * 64

    # reference count
    assert cat.chunk_reference_count("a" * 64) == 1

    # add another file referencing same chunk
    file2 = cat.add_file(snap.id, "bar.txt", 50)
    cat.link_file_chunk(file2, "a" * 64, 0, 0)
    assert cat.chunk_reference_count("a" * 64) == 2

    cat.close()
