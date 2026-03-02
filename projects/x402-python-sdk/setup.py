#!/usr/bin/env python3
"""
x402 Python SDK - 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="x402-sdk",
    version="1.0.0",
    description="x402 协议 Python SDK - 让 Python 开发者轻松集成 HTTP 402 支付协议",
    long_description=long_description,
    author="Martin (紫微智控)",
    author_email="pandac00@163.com",
    url="https://github.com/ziwei/x402-python-sdk",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Payment Processing",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
    ],
    python_requires=">=3.6",
    keywords=[
        "x402", "payment", "http402", "api", "crypto",
        "usdc", "web3", "ai", "agents", "machine-economy"
    ],
    project_urls={
        "Bug Reports": "https://github.com/ziwei/x402-python-sdk/issues",
        "Source": "https://github.com/ziwei/x402-python-sdk",
        "Documentation": "https://github.com/ziwei/x402-python-sdk",
    },
)