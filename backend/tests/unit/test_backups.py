import os
import time

from infrastructure.monitoring.backups import get_latest_backup


def test_get_latest_backup_returns_newest_matching_archive(tmp_path):
    older = tmp_path / "fotabo_hashi_20260101_020000.dump"
    newer = tmp_path / "fotabo_hashi_20260102_020000.dump"
    ignored = tmp_path / "notes.txt"
    older.write_bytes(b"older")
    newer.write_bytes(b"newer")
    ignored.write_text("not a backup")
    os.utime(older, (time.time() - 60, time.time() - 60))

    assert get_latest_backup(str(tmp_path)) == newer


def test_get_latest_backup_returns_none_for_missing_or_empty_directory(tmp_path):
    assert get_latest_backup(str(tmp_path / "missing")) is None
    assert get_latest_backup(str(tmp_path)) is None
