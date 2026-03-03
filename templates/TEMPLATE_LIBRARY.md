# 紫微智控 - 项目模板库

## 📋 模板列表

### 1️⃣ CLI 工具模板
**适用**: 命令行工具、实用脚本

**结构**:
```
project/
├── src/
│   └── main.py
├── tests/
│   └── test_main.py
├── docs/
│   └── README.md
├── requirements.txt
└── spec.md
```

**核心代码模板**:
```python
#!/usr/bin/env python3
"""
{project_name} - v{version}
{description}
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("input", help="输入文件/目录")
    parser.add_argument("-o", "--output", help="输出文件/目录")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细模式")
    parser.add_argument("--version", action="version", version="%(prog)s {version}")
    
    args = parser.parse_args()
    
    # 主逻辑
    process(args.input, args.output, args.verbose)

if __name__ == "__main__":
    main()
```

---

### 2️⃣ Web 应用模板
**适用**: Flask/FastAPI Web 应用

**结构**:
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── templates/
├── tests/
├── docs/
├── requirements.txt
└── config.py
```

**核心代码模板**:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{project_name}", version="{version}")

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
async def root():
    return {"message": "Welcome to {project_name}"}

@app.post("/items/")
async def create_item(item: Item):
    return item
```

---

### 3️⃣ API 服务模板
**适用**: RESTful API、微服务

**结构**:
```
project/
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   └── schemas/
│   └── __init__.py
├── core/
│   ├── config.py
│   └── security.py
├── tests/
└── requirements.txt
```

---

### 4️⃣ 机器人模板
**适用**: Telegram/Discord 机器人、自动化脚本

**结构**:
```
project/
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   ├── services/
│   └── utils/
├── config/
│   └── settings.py
├── tests/
└── requirements.txt
```

---

### 5️⃣ 数据分析模板
**适用**: 数据处理、分析、可视化

**结构**:
```
project/
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
├── src/
│   ├── data_loader.py
│   ├── analyzer.py
│   └── visualizer.py
├── notebooks/
├── tests/
└── requirements.txt
```

---

## 🎯 模板选择逻辑

```python
def select_template(spec_text):
    """根据说明书选择模板"""
    
    templates = {
        'cli_tool': ['工具', '命令行', 'batch', 'rename', 'convert'],
        'web_app': ['网站', 'web', 'Flask', 'FastAPI', '页面'],
        'api_service': ['API', 'REST', '服务', 'endpoint'],
        'bot': ['机器人', 'bot', 'Telegram', 'Discord', '自动'],
        'data_analysis': ['分析', 'data', '统计', '可视化', 'chart']
    }
    
    scores = {}
    for template, keywords in templates.items():
        score = sum(1 for kw in keywords if kw.lower() in spec_text.lower())
        scores[template] = score
    
    return max(scores, key=scores.get) if any(scores.values()) else 'cli_tool'
```

---

## 📦 使用方式

```bash
# 创建项目时自动选择模板
python3 intelligent_creator.py spec.md

# 手动指定模板
python3 intelligent_creator.py spec.md --template cli_tool
```
