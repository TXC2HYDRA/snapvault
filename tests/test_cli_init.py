from pathlib import Path

from click.testing import CliRunner

from snapvault.cli import main


def test_init_creates_expected_repository_structure(tmp_path: Path) -> None:
    repo_path = tmp_path / "snapvault_repo"
    runner = CliRunner()

    result = runner.invoke(main, ["init", str(repo_path)])

    assert result.exit_code == 0
    assert repo_path.exists()
    assert (repo_path / "metadata").is_dir()
    assert "Initialized SnapVault repository" in result.output
