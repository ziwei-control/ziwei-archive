#!/usr/bin/env python3
"""
紫微智控 - 自动化审计系统
安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="ziwei-audit-system",
    version="1.0.0",
    description="紫微智控 - 全面自动化审计系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="紫微智控",
    author_email="pandac00@163.com",
    url="https://github.com/ziwei-control/ziwei-audit-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "ziwei-audit=audit_ziwei_system:main",
        ],
    },
    keywords="audit security code-quality python automation",
)
