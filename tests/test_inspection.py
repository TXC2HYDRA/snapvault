from pathlib import Path

from click.testing import CliRunner

from snapvault.cli import main
from snapvault.snapshot import backup


def test_inspection_list_and_show(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "hello.txt").write_text("hello")

    repo = tmp_path / "repo"
    repo.mkdir()
    backup(source, repo, tag="inspect")

    runner = CliRunner()
    list_result = runner.invoke(main, ["list", str(repo)])
    assert list_result.exit_code == 0
    assert "inspect" in list_result.output

    # show should list the backed-up file path and size
    show_result = runner.invoke(main, ["show", "1", str(repo)])
    assert show_result.exit_code == 0
    assert "hello.txt" in show_result.output
    assert "5" in show_result.output
