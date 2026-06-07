from pathlib import Path

from snapvault.snapshot import backup, restore


def test_backup_and_restore_end_to_end(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_bytes(b"hello world")
    (source / "sub").mkdir()
    (source / "sub" / "b.bin").write_bytes(b"x" * 2048)

    repo = tmp_path / "repo"
    repo.mkdir()

    snap_id = backup(source, repo, tag="test")

    restore_target = tmp_path / "restored"
    restore(snap_id, restore_target, repo)

    assert (restore_target / "a.txt").read_bytes() == b"hello world"
    assert (restore_target / "sub" / "b.bin").read_bytes() == b"x" * 2048
