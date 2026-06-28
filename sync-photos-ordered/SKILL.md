---
name: sync-photos-ordered
description: Export or synchronize Apple Photos library items to a normal folder or external drive while preserving the Photos "Library / All Photos" order with numeric filename prefixes. Use when the user asks to copy, back up, sort, organize, export, or sync Photos.app photos/videos/Live Photos in exact Photos order, especially to Finder or an external disk, with original resources, Live Photo sidecars, resumable progress, and final integrity checks.
---

# Sync Photos Ordered

## Overview

Use this skill to export Apple Photos library assets into a Finder folder with stable numeric prefixes such as `000001_original-name_UUID.heic`. Prefer direct read-only access to the Photos library database and `originals/` resources for speed; fall back to Photos AppleScript export only when database access is unavailable.

## Required Clarifications

Confirm these before writing many files:

- Source: the user usually means the open Photos.app library, not `/System/Applications/Photos.app`. Default to `~/Pictures/Photos Library.photoslibrary` unless they provide another `.photoslibrary`.
- Order: ask which Photos view/order. For "图库/所有照片", use `ZASSET order by ZDATECREATED asc, Z_PK asc`, and verify the first few items against `osascript 'tell application "Photos" to ...'` when possible.
- Target: confirm the exact path, including spaces and punctuation. Similar Chinese folder names can differ by one invisible-looking space.
- Existing files: decide whether to resume, clear, or create a new folder. Default to resume from the largest existing six-digit prefix.
- Naming: include both the numeric prefix and the user-facing original filename when available, then include the library resource filename/UUID for uniqueness. Prefer `ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME`; fall back to `ZCLOUDMASTER.ZORIGINALFILENAME`, then `ZASSET.ZFILENAME`.
- Live Photo policy: preserve original still image and motion video sidecar together under the same numeric prefix.

## Fast Workflow

1. Confirm the Photos library and target path.
2. Ensure the agent has macOS privacy permission to read the Photos library package and write to the target. If `find '<library>/database'` returns "Operation not permitted", ask the user to grant Codex/Terminal Full Disk Access or Photos access, then retry.
3. Run the bundled script in dry-run mode first:

```bash
python3 scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/Drive/Ordered Photos" \
  --dry-run
```

4. If the dry run reports the expected count and start index, run without `--dry-run`.
5. Validate the result with `--verify-only`.

```bash
python3 scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/Drive/Ordered Photos" \
  --verify-only
```

## Script Behavior

Use `scripts/export_photos_ordered.py` for the main export. It:

- Opens `database/Photos.sqlite` read-only.
- Selects non-trashed assets in Photos "All Photos" chronological order.
- Copies primary originals from `originals/<ZDIRECTORY>/<ZFILENAME>`.
- Copies same-stem sidecars from the same originals directory, such as Live Photo `*_3.mov`.
- Names files with the original import filename when Photos has it, making later Finder searches by names like `IMG_0105` work.
- Resumes from the largest existing `000001_` style prefix in the target.
- Writes a progress log in the target by default.
- Verifies distinct prefixes, min/max prefix, missing prefixes, and zero-file warnings.

Use `scripts/rename_existing_export.py` when the target folder was already exported with numeric prefixes but filenames do not include Photos' original import names. Run it without `--apply` first, inspect the preview and counts, then rerun with `--apply`.

Default filename format:

```text
000001_ORIGINAL-FILENAME_LIBRARY-RESOURCE-FILENAME.ext
```

If the original filename is unavailable or already identical to the library resource filename, the script uses:

```text
000001_LIBRARY-RESOURCE-FILENAME.ext
```

## Fallback Workflow

If direct database access is blocked and the user cannot grant permission, use Photos AppleScript export with `using originals`. Warn that it is much slower because Photos exports item by item. Preserve resumability with the same prefix convention and keep progress logs.

## Final Response Checklist

Report:

- Target path
- Photos item count
- Numbered file/component count
- Distinct prefix count
- Prefix range
- Missing prefix count
- Warning count
- Target size when useful

Mention any limitations plainly, especially if macOS permissions prevented database access or if the export used the slower Photos AppleScript fallback.
