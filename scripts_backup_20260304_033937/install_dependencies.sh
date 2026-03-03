#!/bin/bash
# 紫微智控 - 依赖安装脚本

echo "🚀 安装紫微智控系统依赖..."

# 核心依赖
pip3 install -q networkx pytest

# 可选依赖（如果有 API 配置）
# pip3 install brave-search google-api-python-client

echo "✅ 依赖安装完成"
