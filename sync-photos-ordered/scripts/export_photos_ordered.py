#!/usr/bin/env python3
import argparse
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Optional


PREFIX_RE = re.compile(r"^(\d{6})_")


def safe_name(value: str) -> str:
    value = (value or "").strip()
    value = value.replace("/", "_").replace(":", "_")
    value = re.sub(r"[\r\n\t]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def existing_max_prefix(target: Path) -> int:
    max_prefix = 0
    if not target.exists():
        return 0
    for path in target.iterdir():
        if not path.is_file():
            continue
        match = PREFIX_RE.match(path.name)
        if match:
            max_prefix = max(max_prefix, int(match.group(1)))
    return max_prefix


def copy_file(src: Path, dst: Path) -> None:
    shutil.copyfile(src, dst)
    try:
        shutil.copystat(src, dst, follow_symlinks=True)
    except OSError:
        pass


def asset_files(originals: Path, directory: str, filename: str) -> list[Path]:
    primary = originals / directory / filename
    files: list[Path] = []
    if primary.exists():
        files.append(primary)

    parent = primary.parent
    if parent.exists():
        for candidate in sorted(parent.glob(f"{primary.stem}_*")):
            if candidate.is_file() and candidate not in files:
                files.append(candidate)
    return files


def output_name(prefix: str, src: Path, original_filename: Optional[str]) -> str:
    resource_name = safe_name(src.name)
    original = safe_name(original_filename or "")
    if original and original != resource_name:
        original_stem = Path(original).stem
        return f"{prefix}_{original_stem}_{resource_name}"
    return f"{prefix}_{resource_name}"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 10000):
        candidate = path.with_name(f"{stem}_copy{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Too many duplicate filenames for {path}")


def load_rows(library: Path) -> list[tuple[int, str, str, Optional[str]]]:
    db = library / "database" / "Photos.sqlite"
    query = """
        select
            a.Z_PK,
            a.ZDIRECTORY,
            a.ZFILENAME,
            coalesce(aa.ZORIGINALFILENAME, cm.ZORIGINALFILENAME, a.ZFILENAME) as ZORIGINALFILENAME
        from ZASSET a
        left join ZADDITIONALASSETATTRIBUTES aa on aa.Z_PK = a.ZADDITIONALATTRIBUTES
        left join ZCLOUDMASTER cm on cm.Z_PK = a.ZMASTER
        where coalesce(a.ZTRASHEDSTATE, 0) = 0
        order by a.ZDATECREATED asc, a.Z_PK asc
    """
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
        return conn.execute(query).fetchall()


def verify(target: Path, expected_total: int, log_path: Optional[Path]) -> int:
    prefixes: set[int] = set()
    numbered_files = 0
    for path in target.iterdir():
        if not path.is_file():
            continue
        match = PREFIX_RE.match(path.name)
        if match:
            prefixes.add(int(match.group(1)))
            numbered_files += 1

    missing = [i for i in range(1, expected_total + 1) if i not in prefixes]
    warnings: list[str] = []
    if log_path and log_path.exists():
        warnings = [
            line
            for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if "WARNING" in line or "files=0" in line
        ]

    print(f"numbered_files {numbered_files}")
    print(f"distinct_prefixes {len(prefixes)}")
    print(f"min_prefix {min(prefixes) if prefixes else None}")
    print(f"max_prefix {max(prefixes) if prefixes else None}")
    print(f"missing_count {len(missing)}")
    print(f"first_missing {missing[:10]}")
    print(f"warnings_count {len(warnings)}")
    return 0 if len(prefixes) == expected_total and not missing and not warnings else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Apple Photos originals in Photos order.")
    parser.add_argument("--library", required=True, type=Path, help="Path to .photoslibrary")
    parser.add_argument("--target", required=True, type=Path, help="Output folder")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without copying")
    parser.add_argument("--verify-only", action="store_true", help="Only verify an existing export")
    parser.add_argument("--log", type=Path, help="Progress log path; defaults to target/photos_ordered_export.log")
    args = parser.parse_args()

    library = args.library.expanduser()
    target = args.target.expanduser()
    originals = library / "originals"
    log_path = args.log.expanduser() if args.log else target / "photos_ordered_export.log"

    rows = load_rows(library)
    total = len(rows)

    if args.verify_only:
        return verify(target, total, log_path)

    start = existing_max_prefix(target) + 1
    print(f"Library: {library}")
    print(f"Target: {target}")
    print(f"Total Photos media items: {total}")
    print(f"Starting at item: {start}")

    if args.dry_run:
        for index, (_pk, directory, filename, original_filename) in enumerate(rows[start - 1 : start + 4], start=start):
            files = asset_files(originals, directory, filename)
            names = [output_name(f"{index:06d}", src, original_filename) for src in files]
            print(index, filename, "files=", len(files), names)
        return 0

    target.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"Library: {library}\n")
        log.write(f"Target: {target}\n")
        log.write(f"Total Photos media items: {total}\n")
        log.write(f"Starting at item: {start}\n")

    for index, (_pk, directory, filename, original_filename) in enumerate(rows, start=1):
        if index < start:
            continue

        prefix = f"{index:06d}"
        files = asset_files(originals, directory, filename)
        exported = 0

        for src in files:
            dst = unique_path(target / output_name(prefix, src, original_filename))
            copy_file(src, dst)
            exported += 1

        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"item={index} prefix={prefix} files={exported}\n")

        if exported == 0:
            print(f"WARNING: item {index} exported 0 files")
        elif index % 500 == 0:
            print(f"Progress: {index} / {total}")

    print(f"Done: exported through item {total}")
    return verify(target, total, log_path)


if __name__ == "__main__":
    sys.exit(main())
