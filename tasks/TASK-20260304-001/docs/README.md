# 文件批量重命名工具 v1.0

## 📋 简介

一个强大的 Python 命令行工具，支持批量重命名文件，提供多种命名模式和预览功能。

## ✨ 功能特性

- ✅ 按前缀重命名（file_001.txt, file_002.txt）
- ✅ 按日期重命名（20260304_001.txt）
- ✅ 添加后缀（photo_v1.jpg）
- ✅ 预览模式（dry-run）
- ✅ 自动备份
- ✅ 支持撤销操作
- ✅ 文件类型过滤
- ✅ 递归处理子目录
- ✅ 文件名冲突检测
- ✅ 操作日志记录

## 🚀 快速开始

### 安装

```bash
# 无需安装，直接运行
python3 batch_renamer.py --help
```

### 基本用法

```bash
# 按前缀重命名
python3 batch_renamer.py /path/to/dir --prefix "file"

# 按日期重命名
python3 batch_renamer.py /path/to/dir --date

# 添加后缀
python3 batch_renamer.py /path/to/dir --suffix "_v1"

# 预览模式（推荐先用）
python3 batch_renamer.py /path/to/dir --prefix "img" --dry-run

# 只处理特定类型文件
python3 batch_renamer.py /path/to/dir --prefix "photo" --ext .jpg .png

# 递归处理子目录
python3 batch_renamer.py /path/to/dir --prefix "doc" --recursive
```

## 📖 参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| directory | - | 要处理的目录（必需） |
| --prefix | -p | 前缀 |
| --date | -d | 按日期重命名 |
| --suffix | -s | 后缀 |
| --dry-run | -n | 预览模式 |
| --ext | -e | 文件扩展名过滤 |
| --exclude | - | 排除的文件 |
| --recursive | -r | 递归处理子目录 |
| --undo | -u | 撤销上次操作 |

## 🔒 安全特性

1. **自动备份** - 操作前自动备份文件列表到 `.rename_backup.json`
2. **预览模式** - 使用 `--dry-run` 预览效果，不实际执行
3. **冲突检测** - 自动检测文件名冲突
4. **操作日志** - 所有操作记录到 `.rename_log.txt`

## 📝 示例

### 示例 1：整理照片

```bash
# 将照片重命名为 photo_001.jpg, photo_002.jpg...
python3 batch_renamer.py ~/Photos --prefix "photo" --ext .jpg .png --dry-run
```

### 示例 2：按日期归档

```bash
# 按日期重命名文档
python3 batch_renamer.py ~/Documents --date --prefix "doc" --ext .pdf .docx
```

### 示例 3：添加版本后缀

```bash
# 给所有文件添加 v1 后缀
python3 batch_renamer.py ./output --suffix "_v1" --dry-run
```

## ⚠️ 注意事项

1. **先用预览模式** - 首次使用务必加 `--dry-run` 预览
2. **备份重要文件** - 虽然工具有备份，但重要文件建议额外备份
3. **检查冲突** - 工具会自动检测，但也要人工确认

## 📄 许可证

MIT License

## 📞 支持

如有问题，请查看日志文件 `.rename_log.txt`

---

**版本**: 1.0.0  
**生成时间**: 2026-03-04  
**任务 ID**: TASK-20260304-001
