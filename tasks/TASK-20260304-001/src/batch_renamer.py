#!/usr/bin/env python3
# =============================================================================
# 文件批量重命名工具 - v1.0
# 任务 ID: TASK-20260304-001
# 生成时间：2026-03-04
# =============================================================================

import os
import sys
import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class BatchRenamer:
    """文件批量重命名工具"""
    
    def __init__(self, directory: str, dry_run: bool = False):
        self.directory = Path(directory)
        self.dry_run = dry_run
        self.backup_file = self.directory / ".rename_backup.json"
        self.log_file = self.directory / ".rename_log.txt"
        
    def backup_file_list(self, files: List[Path]) -> str:
        """备份文件列表"""
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "directory": str(self.directory),
            "files": [str(f) for f in files]
        }
        
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return str(self.backup_file)
    
    def rename_by_prefix(self, files: List[Path], prefix: str) -> List[Tuple[Path, Path]]:
        """按前缀重命名"""
        changes = []
        for i, file in enumerate(files, 1):
            new_name = f"{prefix}_{i:03d}{file.suffix}"
            new_path = file.parent / new_name
            changes.append((file, new_path))
        return changes
    
    def rename_by_date(self, files: List[Path], prefix: str = "") -> List[Tuple[Path, Path]]:
        """按日期重命名"""
        changes = []
        today = datetime.now().strftime("%Y%m%d")
        for i, file in enumerate(files, 1):
            new_prefix = f"{prefix}_" if prefix else ""
            new_name = f"{new_prefix}{today}_{i:03d}{file.suffix}"
            new_path = file.parent / new_name
            changes.append((file, new_path))
        return changes
    
    def add_suffix(self, files: List[Path], suffix: str) -> List[Tuple[Path, Path]]:
        """添加后缀"""
        changes = []
        for file in files:
            new_name = f"{file.stem}{suffix}{file.suffix}"
            new_path = file.parent / new_name
            changes.append((file, new_path))
        return changes
    
    def filter_files(self, files: List[Path], 
                     extensions: List[str] = None,
                     exclude: List[str] = None,
                     recursive: bool = False) -> List[Path]:
        """过滤文件"""
        if recursive:
            all_files = list(self.directory.rglob("*"))
        else:
            all_files = list(self.directory.glob("*"))
        
        # 只保留文件
        files = [f for f in all_files if f.is_file()]
        
        # 按扩展名过滤
        if extensions:
            files = [f for f in files if f.suffix.lower() in extensions]
        
        # 排除特定文件
        if exclude:
            files = [f for f in files if not any(ex in str(f) for ex in exclude)]
        
        return files
    
    def check_conflicts(self, changes: List[Tuple[Path, Path]]) -> List[str]:
        """检查文件名冲突"""
        conflicts = []
        new_names = set()
        
        for old_path, new_path in changes:
            if new_path in new_names or (new_path.exists() and new_path not in [x[0] for x in changes]):
                conflicts.append(str(new_path))
            new_names.add(new_path)
        
        return conflicts
    
    def preview_changes(self, changes: List[Tuple[Path, Path]]):
        """预览改名效果"""
        print("\n" + "=" * 70)
        print("📋 改名预览")
        print("=" * 70)
        
        for old_path, new_path in changes:
            print(f"  {old_path.name}")
            print(f"    ↓")
            print(f"  {new_path.name}")
            print()
        
        print("=" * 70)
        print(f"共 {len(changes)} 个文件将被重命名")
        print("=" * 70)
    
    def execute_changes(self, changes: List[Tuple[Path, Path]]) -> Dict:
        """执行改名操作"""
        result = {
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for old_path, new_path in changes:
            try:
                if not self.dry_run:
                    shutil.move(str(old_path), str(new_path))
                result["success"] += 1
            except Exception as e:
                result["failed"] += 1
                result["errors"].append(f"{old_path}: {str(e)}")
        
        return result
    
    def log_operation(self, operation: str, result: Dict):
        """记录操作日志"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"时间：{datetime.now().isoformat()}\n")
            f.write(f"操作：{operation}\n")
            f.write(f"成功：{result.get('success', 0)}\n")
            f.write(f"失败：{result.get('failed', 0)}\n")
            if result.get('errors'):
                f.write(f"错误：\n")
                for error in result['errors']:
                    f.write(f"  - {error}\n")


def main():
    parser = argparse.ArgumentParser(
        description="文件批量重命名工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按前缀重命名
  python batch_renamer.py /path/to/dir --prefix "file"
  
  # 按日期重命名
  python batch_renamer.py /path/to/dir --date
  
  # 添加后缀
  python batch_renamer.py /path/to/dir --suffix "_v1"
  
  # 预览模式（不实际执行）
  python batch_renamer.py /path/to/dir --prefix "file" --dry-run
  
  # 只处理 jpg 和 png 文件
  python batch_renamer.py /path/to/dir --prefix "img" --ext .jpg .png
        """
    )
    
    parser.add_argument("directory", help="要处理的目录")
    parser.add_argument("--prefix", "-p", help="前缀")
    parser.add_argument("--date", "-d", action="store_true", help="按日期重命名")
    parser.add_argument("--suffix", "-s", help="后缀")
    parser.add_argument("--dry-run", "-n", action="store_true", help="预览模式")
    parser.add_argument("--ext", "-e", nargs="+", help="文件扩展名过滤")
    parser.add_argument("--exclude", nargs="+", help="排除的文件")
    parser.add_argument("--recursive", "-r", action="store_true", help="递归处理子目录")
    parser.add_argument("--undo", "-u", action="store_true", help="撤销上次操作")
    
    args = parser.parse_args()
    
    # 创建工具实例
    renamer = BatchRenamer(args.directory, dry_run=args.dry_run)
    
    # 过滤文件
    extensions = [f".{e.lstrip('.')}" for e in args.ext] if args.ext else None
    files = renamer.filter_files(
        files=[],
        extensions=extensions,
        exclude=args.exclude,
        recursive=args.recursive
    )
    
    if not files:
        print("❌ 没有找到符合条件的文件")
        return
    
    print(f"✅ 找到 {len(files)} 个文件")
    
    # 备份文件列表
    backup_path = renamer.backup_file_list(files)
    print(f"💾 文件列表已备份：{backup_path}")
    
    # 生成改名方案
    changes = []
    if args.prefix:
        changes = renamer.rename_by_prefix(files, args.prefix)
    elif args.date:
        changes = renamer.rename_by_date(files, args.prefix or "")
    elif args.suffix:
        changes = renamer.add_suffix(files, args.suffix)
    
    if not changes:
        print("❌ 请指定重命名方式 (--prefix, --date, 或 --suffix)")
        return
    
    # 检查冲突
    conflicts = renamer.check_conflicts(changes)
    if conflicts:
        print("❌ 发现文件名冲突:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        return
    
    # 预览
    if args.dry_run:
        renamer.preview_changes(changes)
        print("\n⚠️  这是预览模式，文件未被实际重命名")
        print("   去掉 --dry-run 参数执行实际改名")
    else:
        print("\n🔄 开始重命名...")
        result = renamer.execute_changes(changes)
        renamer.log_operation("批量重命名", result)
        
        print(f"\n✅ 完成！成功：{result['success']}, 失败：{result['failed']}")
        if result['errors']:
            print("\n错误:")
            for error in result['errors']:
                print(f"  - {error}")


if __name__ == "__main__":
    main()
