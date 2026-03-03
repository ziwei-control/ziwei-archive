#!/usr/bin/env python3
"""
文件批量重命名工具 - 单元测试
"""

import unittest
import tempfile
import os
from pathlib import Path
from src.batch_renamer import BatchRenamer


class TestBatchRenamer(unittest.TestCase):
    """测试批量重命名工具"""
    
    def setUp(self):
        """创建测试目录和文件"""
        self.test_dir = tempfile.mkdtemp()
        self.renamer = BatchRenamer(self.test_dir, dry_run=True)
        
        # 创建测试文件
        for i in range(5):
            Path(self.test_dir, f"test_{i}.txt").touch()
    
    def tearDown(self):
        """清理测试文件"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_filter_files(self):
        """测试文件过滤"""
        files = self.renamer.filter_files([])
        self.assertEqual(len(files), 5)
    
    def test_rename_by_prefix(self):
        """测试按前缀重命名"""
        files = list(Path(self.test_dir).glob("*.txt"))
        changes = self.renamer.rename_by_prefix(files, "file")
        
        self.assertEqual(len(changes), 5)
        self.assertTrue(changes[0][1].name.startswith("file_"))
    
    def test_rename_by_date(self):
        """测试按日期重命名"""
        files = list(Path(self.test_dir).glob("*.txt"))
        changes = self.renamer.rename_by_date(files, "doc")
        
        self.assertEqual(len(changes), 5)
        self.assertIn("20260304", changes[0][1].name)
    
    def test_add_suffix(self):
        """测试添加后缀"""
        files = list(Path(self.test_dir).glob("*.txt"))
        changes = self.renamer.add_suffix(files, "_v1")
        
        self.assertEqual(len(changes), 5)
        self.assertIn("_v1", changes[0][1].name)
    
    def test_check_conflicts(self):
        """测试冲突检测"""
        files = list(Path(self.test_dir).glob("*.txt"))
        changes = [(f, f) for f in files]  # 故意制造冲突
        conflicts = self.renamer.check_conflicts(changes)
        
        self.assertGreater(len(conflicts), 0)


if __name__ == "__main__":
    unittest.main()
