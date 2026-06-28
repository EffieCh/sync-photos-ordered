#!/usr/bin/env python3
import argparse
import re
import sqlite3
from pathlib import Path
from typing import Optional

PREFIX_RE = re.compile(r"^(\d{6})_(.+)$")


def safe_name(value: str) -> str:
    value = (value or "").strip()
    value = value.replace("/", "_").replace(":", "_")
    value = re.sub(r"[\r\n\t]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def load_original_names(library: Path) -> dict[int, str]:
    db = library / "database" / "Photos.sqlite"
    query = """
        select
            coalesce(aa.ZORIGINALFILENAME, cm.ZORIGINALFILENAME, a.ZFILENAME) as original_name
        from ZASSET a
        left join ZADDITIONALASSETATTRIBUTES aa on aa.Z_PK = a.ZADDITIONALATTRIBUTES
        left join ZCLOUDMASTER cm on cm.Z_PK = a.ZMASTER
        where coalesce(a.ZTRASHEDSTATE, 0) = 0
        order by a.ZDATECREATED asc, a.Z_PK asc
    """
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
        rows = conn.execute(query).fetchall()
    return {index: safe_name(row[0] or "") for index, row in enumerate(rows, start=1)}


def desired_name(current_name: str, original_name: Optional[str]) -> Optional[str]:
    match = PREFIX_RE.match(current_name)
    if not match or not original_name:
        return None

    prefix, rest = match.groups()
    original_stem = Path(original_name).stem
    if not original_stem:
        return None

    rest_stem = Path(rest).stem
    if rest == original_name or rest_stem == original_stem or rest_stem.startswith(f"{original_stem}_"):
        return None

    return f"{prefix}_{original_stem}_{rest}"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 10000):
        candidate = path.with_name(f"{stem}_copy{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Too many duplicate names for {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rename ordered Photos export files to include original filenames.")
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="Perform renames. Without this, only print a dry-run summary.")
    parser.add_argument("--preview", type=int, default=20)
    args = parser.parse_args()

    original_names = load_original_names(args.library.expanduser())
    target = args.target.expanduser()

    planned: list[tuple[Path, Path]] = []
    skipped = 0
    unrecognized = 0

    for path in sorted(target.iterdir()):
        if not path.is_file():
            continue
        match = PREFIX_RE.match(path.name)
        if not match:
            continue
        index = int(match.group(1))
        new_name = desired_name(path.name, original_names.get(index))
        if new_name is None:
            skipped += 1
            continue
        planned.append((path, unique_path(path.with_name(new_name))))

    for src, dst in planned[: args.preview]:
        print(f"{src.name} -> {dst.name}")

    print(f"planned_renames {len(planned)}")
    print(f"skipped_or_already_named {skipped}")
    print(f"unrecognized {unrecognized}")

    if not args.apply:
        print("dry_run true")
        return 0

    for src, dst in planned:
        src.rename(dst)
    print("renamed true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
