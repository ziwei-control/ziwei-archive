# 如意（jiyi）- 紫微智控记忆系统

> 分门别类、最小存储、快速搜索

---

## 🚀 快速开始

### 使用方式

```bash
# 方式 1：直接运行
cd /home/admin/Ziwei/jiyi
python3 jiyi.py <命令> [参数]

# 方式 2：添加别名（推荐）
echo 'alias jiyi="python3 /home/admin/Ziwei/jiyi/jiyi.py"' >> ~/.bashrc
source ~/.bashrc
jiyi <命令> [参数]
```

---

## 📋 命令列表

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `add` | `a` | 添加记忆 | `jiyi add "内容" 分类 标签` |
| `search` | `s`, `find` | 搜索记忆 | `jiyi search 关键词` |
| `list` | `ls` | 列出记忆 | `jiyi list [分类]` |
| `categories` | `cat` | 显示分类 | `jiyi categories` |
| `tags` | - | 显示标签 | `jiyi tags` |
| `version` | `v` | 显示版本 | `jiyi version` |
| `help` | `h` | 显示帮助 | `jiyi help` |

---

## 💡 使用示例

### 添加记忆

```bash
# 自动分类
jiyi add "x402 API 端口是 5002"

# 手动指定分类和标签
jiyi add "x402 API 公网地址 8.213.149.224" 项目 x402 公网

# 添加命令说明
jiyi add "启动 x402 API: cd /home/admin/Ziwei/projects/x402-api && python3 app_production.py" 命令 x402 启动
```

### 搜索记忆

```bash
# 关键词搜索
jiyi search x402

# 交互式搜索
jiyi search
```

### 列出记忆

```bash
# 列出所有
jiyi list

# 按分类列出
jiyi list 命令
jiyi list 项目
```

---

## 📁 数据结构

```
jiyi/
├── index.json          # 分类和标签索引
├── memory/
│   └── m_*.json        # 记忆文件（JSON 格式）
└── jiyi.py             # 主程序
```

### 记忆文件格式

```json
{
  "id": "m_1772217967986981",
  "category": "命令",
  "content": "runtask 是紫微智控一键启动任务命令",
  "tags": ["runtask", "自动化"],
  "created_at": "2026-02-28T02:46:07.986984",
  "updated_at": "2026-02-28T02:46:07.986990",
  "is_new": true
}
```

---

## 🔄 同步 GitHub

```bash
# 从 GitHub 同步最新数据
cd /home/admin/Ziwei
git clone https://github.com/ziwei-control/ziwei-archive.git /tmp/ziwei-github
cp /tmp/ziwei-github/jiyi/index.json /home/admin/Ziwei/jiyi/
cp -r /tmp/ziwei-github/jiyi/memory/* /home/admin/Ziwei/jiyi/memory/
```

---

## 🎯 自动分类规则

系统会根据内容自动分类：

| 分类 | 关键词 |
|------|--------|
| 命令 | 命令，runtask, look, jiyi, 执行 |
| 项目 | 项目，仓库，github, gitee |
| 配置 | 配置，config, env, token |
| 流程 | 流程，步骤，自动，同步 |
| 错误 | 错误，失败，问题，bug |
| 系统 | 系统，服务，监控，进程 |
| 文档 | 文档，说明，readme, sop |

---

## 📊 当前状态

```bash
# 查看统计
jiyi categories
jiyi tags
```

---

**版本：** v1.0.0  
**最后更新：** 2026-03-06
