from pathlib import Path

import click
from .snapshot import backup as snapshot_backup, restore as snapshot_restore
from .catalog import Catalog


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


@main.command(name="backup")
@click.argument("source", type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path))
@click.argument("repo_path", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path))
@click.option("--tag", default=None, help="Snapshot tag")
def backup(source: Path, repo_path: Path, tag: str | None) -> None:
    """Create a backup snapshot of SOURCE into REPO_PATH."""
    snap_id = snapshot_backup(source, repo_path, tag)
    click.echo(f"Created snapshot {snap_id}")


@main.command(name="restore")
@click.argument("snapshot_id", type=int)
@click.argument("target", type=click.Path(file_okay=True, dir_okay=True, path_type=Path))
@click.argument("repo_path", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path))
def restore(snapshot_id: int, target: Path, repo_path: Path) -> None:
    """Restore snapshot SNAPSHOT_ID into TARGET directory from REPO_PATH."""
    snapshot_restore(snapshot_id, target, repo_path)
    click.echo(f"Restored snapshot {snapshot_id} to {target}")


@main.command(name="list")
@click.argument("repo_path", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path))
def list_snapshots(repo_path: Path) -> None:
    """List all snapshots in the repository."""
    catalog = Catalog(repo_path)
    for snapshot in catalog.list_snapshots():
        tag = snapshot.tag or ""
        click.echo(f"{snapshot.id}\t{snapshot.created_at}\t{tag}")
    catalog.close()


@main.command(name="show")
@click.argument("snapshot_id", type=int)
@click.argument("repo_path", type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path))
def show(snapshot_id: int, repo_path: Path) -> None:
    """Show files contained in a snapshot."""
    catalog = Catalog(repo_path)
    files = catalog.get_snapshot_files(snapshot_id)
    for file_id, path, size in files:
        click.echo(f"{file_id}\t{path}\t{size}")
    catalog.close()
