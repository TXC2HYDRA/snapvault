from pathlib import Path

import click
from .snapshot import backup


@click.group()
def main() -> None:
    """SnapVault command line interface."""


@main.command()
@click.argument("repo_path", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path))
def init(repo_path: Path) -> None:
    """Initialize a new SnapVault repository."""
    repo_path.mkdir(parents=True, exist_ok=True)
    metadata_dir = repo_path / "metadata"
    metadata_dir.mkdir(exist_ok=True)
    click.echo(f"Initialized SnapVault repository at {repo_path}")



@main.command()
@click.argument("source", type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path))
@click.argument("repo_path", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path))
@click.option("--tag", default=None, help="Snapshot tag")
def backup_cmd(source: Path, repo_path: Path, tag: str | None) -> None:
    """Create a backup snapshot of SOURCE into REPO_PATH."""
    snap_id = backup(source, repo_path, tag)
    click.echo(f"Created snapshot {snap_id}")
