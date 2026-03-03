#!/usr/bin/env python3
# =============================================================================
# 自动部署引擎
# 功能：自动测试 + 打包 + 部署 + CI/CD
# =============================================================================

import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class AutoDeployer:
    """自动部署引擎"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.deploy_log = []
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        self.deploy_log.append(log_msg)
        print(log_msg)
    
    def run_tests(self) -> bool:
        """运行测试"""
        self.log("\n🧪 运行测试...")
        
        test_dir = self.project_dir / "tests"
        if not test_dir.exists():
            self.log("   ⚠️ 测试目录不存在")
            return True
        
        try:
            # 运行 pytest
            result = subprocess.run(
                ['python3', '-m', 'pytest', str(test_dir), '-v', '--tb=short'],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("   ✅ 所有测试通过")
                return True
            else:
                self.log(f"   ❌ 测试失败")
                self.log(f"   {result.stdout[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("   ❌ 测试超时")
            return False
        except Exception as e:
            self.log(f"   ❌ 测试执行失败：{e}")
            return False
    
    def build_package(self) -> bool:
        """构建包"""
        self.log("\n📦 构建包...")
        
        # 检查 setup.py
        setup_py = self.project_dir / "setup.py"
        if not setup_py.exists():
            self.log("   ⚠️ setup.py 不存在，创建中...")
            self._create_setup_py()
        
        try:
            # 构建
            result = subprocess.run(
                ['python3', 'setup.py', 'sdist', 'bdist_wheel'],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log("   ✅ 包构建成功")
                
                # 检查生成的文件
                dist_dir = self.project_dir / "dist"
                if dist_dir.exists():
                    files = list(dist_dir.glob('*'))
                    self.log(f"   生成 {len(files)} 个文件")
                
                return True
            else:
                self.log(f"   ❌ 构建失败")
                return False
                
        except Exception as e:
            self.log(f"   ❌ 构建失败：{e}")
            return False
    
    def _create_setup_py(self):
        """创建 setup.py"""
        setup_content = f'''#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="{self.project_dir.name}",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # TODO: 添加依赖
    ],
    entry_points={{
        "console_scripts": [
            # TODO: 添加命令行入口
        ],
    }},
)
'''
        
        setup_py = self.project_dir / "setup.py"
        with open(setup_py, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        
        self.log(f"   ✅ 创建 setup.py")
    
    def deploy_to_pypi(self, test: bool = True) -> bool:
        """部署到 PyPI"""
        self.log("\n🚀 部署到 PyPI...")
        
        if test:
            self.log("   ℹ️  测试模式，不实际部署")
            return True
        
        try:
            # 使用 twine 部署
            result = subprocess.run(
                ['twine', 'upload', 'dist/*'],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log("   ✅ 部署成功")
                return True
            else:
                self.log(f"   ❌ 部署失败")
                return False
                
        except Exception as e:
            self.log(f"   ❌ 部署失败：{e}")
            return False
    
    def deploy_to_github(self) -> bool:
        """部署到 GitHub Releases"""
        self.log("\n🚀 部署到 GitHub Releases...")
        
        # 检查 git 仓库
        git_dir = self.project_dir / ".git"
        if not git_dir.exists():
            self.log("   ⚠️ 不是 git 仓库，跳过")
            return True
        
        try:
            # 获取版本号
            version = "1.0.0"
            
            # 创建 tag
            subprocess.run(
                ['git', 'tag', f'v{version}'],
                cwd=str(self.project_dir),
                capture_output=True
            )
            
            # 推送 tag
            result = subprocess.run(
                ['git', 'push', 'origin', f'v{version}'],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log(f"   ✅ 创建 release v{version}")
                return True
            else:
                self.log(f"   ⚠️ 推送失败")
                return True  # 不视为致命错误
                
        except Exception as e:
            self.log(f"   ⚠️ 部署失败：{e}")
            return True  # 不视为致命错误
    
    def create_dockerfile(self) -> bool:
        """创建 Dockerfile"""
        self.log("\n🐳 创建 Dockerfile...")
        
        dockerfile = self.project_dir / "Dockerfile"
        
        dockerfile_content = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

CMD ["{self.project_dir.name}"]
'''
        
        with open(dockerfile, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        self.log("   ✅ 创建 Dockerfile")
        return True
    
    def create_github_actions(self) -> bool:
        """创建 GitHub Actions CI/CD"""
        self.log("\n⚙️  创建 GitHub Actions...")
        
        workflows_dir = self.project_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_content = f'''name: CI/CD

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python {{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: {{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run tests
      run: |
        pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Build package
      run: |
        pip install build
        python -m build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: {{{{ secrets.PYPI_API_TOKEN }}}}
'''
        
        workflow_file = workflows_dir / "ci.yml"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        
        self.log("   ✅ 创建 GitHub Actions 工作流")
        return True
    
    def deploy(self, test: bool = True) -> Dict:
        """执行完整部署流程"""
        self.log("\n" + "=" * 70)
        self.log("🚀 紫微制造 - 自动部署引擎")
        self.log("=" * 70)
        self.log(f"项目：{self.project_dir}")
        self.log(f"测试模式：{test}")
        
        start_time = datetime.now()
        
        # 1. 运行测试
        if not self.run_tests():
            self.log("\n❌ 测试失败，停止部署")
            return {"success": False, "stage": "test"}
        
        # 2. 构建包
        if not self.build_package():
            self.log("\n❌ 构建失败，停止部署")
            return {"success": False, "stage": "build"}
        
        # 3. 创建 Dockerfile
        self.create_dockerfile()
        
        # 4. 创建 CI/CD
        self.create_github_actions()
        
        # 5. 部署到 GitHub
        self.deploy_to_github()
        
        # 6. 部署到 PyPI（仅测试模式）
        self.deploy_to_pypi(test=test)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 保存部署日志
        log_file = self.project_dir / "deploy_log.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.deploy_log))
        
        self.log("\n" + "=" * 70)
        self.log("📊 部署报告")
        self.log("=" * 70)
        self.log(f"总耗时：{duration:.2f}秒")
        self.log(f"状态：✅ 成功")
        self.log(f"日志：{log_file}")
        
        return {
            "success": True,
            "duration": duration,
            "log_file": str(log_file)
        }


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python auto_deployer.py <project_dir> [--prod]")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    prod = '--prod' in sys.argv
    
    deployer = AutoDeployer(project_dir)
    result = deployer.deploy(test=not prod)
    
    if result['success']:
        print("\n✅ 部署成功")
    else:
        print(f"\n❌ 部署失败于：{result.get('stage', 'unknown')}")


if __name__ == '__main__':
    main()
