#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    project_root = Path(__file__).resolve().parent
    if os.name == "nt":
        project_python = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        project_python = project_root / ".venv" / "bin" / "python"

    # Make `python manage.py ...` use this project's dependencies even when
    # the shell's `python` points to the system interpreter.
    if (
        project_python.is_file()
        and project_python.resolve() != Path(sys.executable).resolve()
    ):
        raise SystemExit(
            subprocess.call(
                [str(project_python), str(Path(__file__).resolve()), *sys.argv[1:]]
            )
        )

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.development",
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
