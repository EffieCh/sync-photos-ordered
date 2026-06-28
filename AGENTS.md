# Agent Guidance

This repository contains standalone Python scripts for exporting Apple Photos libraries in Photos "Library / All Photos" order.

Use these instructions for any local coding agent or automation environment that can run shell commands, including but not limited to agentic coding tools, IDE assistants, and terminal-based assistants.

The scripts are the primary interface. The included Codex skill folder is optional metadata for Codex users.

## Core Commands

Dry-run:

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos" \
  --dry-run
```

Export:

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos"
```

Verify:

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos" \
  --verify-only
```

Rename an existing ordered export to include original Photos filenames:

```bash
python3 sync-photos-ordered/scripts/rename_existing_export.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos"
```

Add `--apply` only after reviewing the dry-run summary.

## Safety

- Confirm the exact `.photoslibrary` path and target folder before writing.
- Run dry-run first.
- The export script reads `Photos.sqlite` in read-only mode.
- The export script copies from the Photos library `originals/` directory and writes to the target folder.
- The rename script only renames files in the target folder.
- If macOS returns `Operation not permitted`, ask the user to grant Full Disk Access to the app or terminal running the agent.
- Be careful with external drives and folder names that contain spaces, punctuation, or lookalike characters.
