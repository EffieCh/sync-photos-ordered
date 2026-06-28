# Sync Photos Ordered

A macOS Apple Photos export utility that preserves the Photos **Library / All Photos** order.

一个 macOS Apple Photos 导出工具，用来严格保留“照片”App 中 **图库 / 所有照片** 的顺序。

It is designed for large macOS Photos libraries that need to be edited, backed up, searched, or processed outside Photos.app. It copies original resources, keeps Live Photo components together, and names files with stable numeric prefixes plus the original import filename when Photos has it.

适合把大型 Apple Photos 图库导出到普通 Finder 文件夹，方便备份、剪辑、搜索或交给其他工具处理。它会复制原始资源，尽量保留 Live Photo 的照片和视频组件，并使用稳定的数字前缀加原始文件名来命名。

The Python scripts are standalone. You can use them directly from Terminal or through any local coding agent that can run shell commands. The repository also includes optional agent metadata, including a Codex skill folder.

这些 Python 脚本是独立工具，可以直接在 Terminal 里使用，也可以被任何能运行本地命令的 AI coding agent 调用。本仓库也附带可选的 agent 元数据，包括 Codex skill 文件夹。

## What It Does / 功能

- Exports Apple Photos items in Photos "All Photos" chronological order.  
  按 Apple Photos “所有照片”的时间顺序导出项目。
- Preserves photos, videos, and Live Photo sidecars such as `*_3.mov`.  
  保留照片、视频，以及 Live Photo 的 sidecar 视频，例如 `*_3.mov`。
- Produces Finder-sortable and search-friendly filenames.  
  生成可在 Finder 中稳定排序、也方便搜索的文件名。

```text
000001_IMG_0105_29F7FAF6-02C9-4A48-9398-7780D31CF8D2.heic
000001_IMG_0105_29F7FAF6-02C9-4A48-9398-7780D31CF8D2_3.mov
```

- Resumes from the largest existing six-digit prefix in the target folder.  
  支持续跑：会从目标文件夹中已有的最大六位数字前缀后继续。
- Verifies missing prefixes and zero-file warnings.  
  支持校验缺号和 0 文件警告。
- Includes a helper to rename an existing ordered export so filenames include Photos' original filename metadata.  
  包含一个辅助脚本，可给已导出的有序文件补上 Photos 记录里的原始文件名。

## Requirements / 要求

- macOS with Apple Photos.  
  macOS，并且使用 Apple Photos。
- Python 3.9+.  
  Python 3.9 或更新版本。
- A local `.photoslibrary`, usually:  
  一个本地 `.photoslibrary`，通常是：

```text
~/Pictures/Photos Library.photoslibrary
```

- Permission to read the Photos library package and write to the destination folder.  
  需要有权限读取 Photos 图库包，并写入目标文件夹。

If macOS reports `Operation not permitted`, open **System Settings -> Privacy & Security -> Full Disk Access** and grant access to the terminal or app running the script.

如果 macOS 报错 `Operation not permitted`，请打开 **系统设置 -> 隐私与安全性 -> 完全磁盘访问权限**，给运行脚本的 Terminal 或 App 授权。

## Use With Coding Agents / 给 AI Coding Agents 使用

The scripts are agent-agnostic. Any local coding agent or automation environment can run:

这些脚本不依赖任何特定 AI 工具。任何本地 coding agent 或自动化环境都可以运行：

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py --help
python3 sync-photos-ordered/scripts/rename_existing_export.py --help
```

For agent-specific guidance, see `AGENTS.md`.  
通用 agent 操作说明见 `AGENTS.md`。

For Codex users, this repository also includes a skill folder at `sync-photos-ordered/`.  
Codex 用户也可以把 `sync-photos-ordered/` 作为 skill 使用。

## Install As A Codex Skill / 作为 Codex Skill 安装

Clone this repository and copy the skill folder into your Codex skills directory:

克隆本仓库，并把 skill 文件夹复制到 Codex skills 目录：

```bash
git clone https://github.com/YOUR-USERNAME/sync-photos-ordered.git
mkdir -p ~/.codex/skills
cp -R sync-photos-ordered/sync-photos-ordered ~/.codex/skills/
```

Then invoke it in Codex with:

然后在 Codex 里这样调用：

```text
Use $sync-photos-ordered to export my Photos library to an external drive in Photos order.
```

## Use The Script Directly / 直接使用脚本

Dry-run first:

先 dry-run，确认不会写错位置：

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos" \
  --dry-run
```

Export:

正式导出：

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos"
```

Verify:

校验导出结果：

```bash
python3 sync-photos-ordered/scripts/export_photos_ordered.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos" \
  --verify-only
```

Rename an existing ordered export to include original filenames:

给已有的有序导出结果补上原始文件名：

```bash
python3 sync-photos-ordered/scripts/rename_existing_export.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos"
```

Apply the rename after reviewing the dry-run summary:

检查 dry-run 摘要后，再加 `--apply` 执行重命名：

```bash
python3 sync-photos-ordered/scripts/rename_existing_export.py \
  --library "$HOME/Pictures/Photos Library.photoslibrary" \
  --target "/Volumes/YourDrive/Ordered Photos" \
  --apply
```

## Safety Notes / 安全说明

The export script opens `Photos.sqlite` read-only and copies files from the Photos library `originals/` directory. It does not modify the Photos library.

导出脚本会以只读方式打开 `Photos.sqlite`，并从 Photos 图库的 `originals/` 目录复制文件。它不会修改 Photos 图库。

The rename helper only renames files in the target folder. It does not touch the Photos library.

重命名脚本只会重命名目标文件夹里的文件，不会触碰 Photos 图库。

Always dry-run first, especially before writing to an external drive.

请始终先 dry-run，尤其是在写入外接硬盘之前。

## License / 许可证

MIT
