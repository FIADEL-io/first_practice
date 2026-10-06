import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AppConfig:

    vfs_path: Path
    script_path: Optional[Path] = None


def parse_args(argv: Optional[list[str]] = None) -> AppConfig:

    parser = argparse.ArgumentParser(
        description="VFS Emulator — эмулятор командной оболочки UNIX.",
        prog="vfs-emulator",
    )
    parser.add_argument(
        "--vfs-path",
        type=Path,
        required=True,
        help="Путь к физическому расположению VFS.",
    )
    parser.add_argument(
        "--script-path",
        type=Path,
        default=None,
        help="Путь к стартовому скрипту (опционально).",
    )

    args = parser.parse_args(argv)
    return AppConfig(vfs_path=args.vfs_path, script_path=args.script_path)
