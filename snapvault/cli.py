from pathlib import Path

import click


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
