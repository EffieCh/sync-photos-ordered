# Sync Photos Ordered

A macOS Apple Photos export utility that preserves the Photos **Library / All Photos** order.

It is designed for large macOS Photos libraries that need to be edited, backed up, or searched outside Photos.app. It copies original resources, keeps Live Photo components together, and names files with stable numeric prefixes plus the original import filename when Photos has it.

The Python scripts are standalone. You can use them directly from Terminal or through any local coding assistant that can run shell commands. The repository also includes optional agent metadata, including a Codex skill folder.

## What It Does

- Exports Apple Photos items in Photos "All Photos" chronological order.
- Preserves photos, videos, and Live Photo sidecars such as `*_3.mov`.
- Produces Finder-sortable names like:

```text
000001_IMG_0105_29F7FAF6-02C9-4A48-9398-7780D31CF8D2.heic
000001_IMG_0105_29F7FAF6-02C9-4A48-9398-7780D31CF8D2_3.mov
```

- Resumes from the largest existing six-digit prefix in the target folder.
- Verifies missing prefixes and zero-file warnings.
- Includes a helper to rename an existing ordered export so filenames include Photos' original filename metadata.

## Requirements

- macOS with Apple Photos.
- Python 3.9+.
- A local `.photoslibrary`, usually:

```text
~/Pictures/Photos Library.photoslibrary
```

- Permission to read the Photos library package and write to the destination folder.

If macOS reports `Operation not permitted`, open **System Settings -> Privacy & Security -> Full Disk Access** and grant access to the terminal or app running the script.

## Use With Coding Agents

The scripts are agent-agnostic. Any local coding agent or automation environment can run:

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py --help
python3 sync-photos-ordered/scripts/rename_existing_export.py --help
```

For agent-specific guidance, see `AGENTS.md`.

For Codex users, this repository also includes a skill folder at `sync-photos-ordered/`.

## Install As A Codex Skill

Clone this repository and copy the skill folder into your Codex skills directory:

```bash
git clone https://github.com/YOUR-USERNAME/sync-photos-ordered.git
mkdir -p ~/.codex/skills
cp -R sync-photos-ordered/sync-photos-ordered ~/.codex/skills/
```

Then invoke it in Codex with:

```text
Use $sync-photos-ordered to export my Photos library to an external drive in Photos order.
```

## Use The Script Directly

Dry-run first:

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

Rename an existing ordered export to include original filenames:

```bash
python3 sync-photos-ordered/scripts/rename_existing_export.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos"
```

Apply the rename after reviewing the dry-run summary:

```bash
python3 sync-photos-ordered/scripts/rename_existing_export.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos" \
  --apply
```

## Safety Notes

The export script opens `Photos.sqlite` read-only and copies files from the Photos library `originals/` directory. It does not modify the Photos library.

The rename helper only renames files in the target folder. It does not touch the Photos library.

Always dry-run first, especially before writing to an external drive.

## License

MIT
