from pathlib import Path


def get_latest_backup(backup_dir: str) -> Path | None:
    """Return the latest local custom-format backup, if one exists."""
    directory = Path(backup_dir)
    if not directory.is_dir():
        return None

    backups = sorted(
        directory.glob("fotabo_hashi_*.dump"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return backups[0] if backups else None
