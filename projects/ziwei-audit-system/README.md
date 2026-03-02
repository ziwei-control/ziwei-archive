# 🔍 紫微智控 - 自动化审计系统

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-green.svg)](https://github.com/ziwei-control/ziwei-audit-system)

一套**全面、自动化、可定制**的代码和安全审计工具，用于监控和评估系统的健康状态、安全性和代码质量。

---

## ✨ 核心功能

- 🔍 **项目结构审计** - 自动扫描项目，统计文件信息
- 🏃 **运行服务审计** - 检测正在运行的服务进程
- 🔒 **安全审计** - 检测硬编码密码、API Key 泄露、代码注入风险
- 📊 **代码质量审计** - 统计代码行数、函数/类数量
- ⚙️ **配置文件审计** - 检查.env 权限、.gitignore 配置
- 📦 **Git 仓库审计** - 自动识别 Git 仓库
- 💾 **磁盘使用审计** - 分析空间使用情况
- 📄 **审计报告生成** - JSON + Markdown 双格式报告

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/ziwei-control/ziwei-audit-system.git
cd ziwei-audit-system

# 无需额外依赖（使用 Python 标准库）
```

### 使用

```bash
# 运行审计
python3 src/audit_ziwei_system.py

# 指定审计目录
python3 src/audit_ziwei_system.py /path/to/your/project

# 查看帮助
python3 src/audit_ziwei_system.py --help
```

### 输出示例

```
======================================================================
🔍 紫微智控系统 - 全面审计
======================================================================

📁 项目结构审计
✅ x402-api                  | 文件：  32 | Python:  20 | 111.4 KB
✅ x402-python-sdk           | 文件：  16 | Python:   8 | 35.1 KB

🔒 安全审计
⚠️  发现 7 个安全问题

📊 代码质量审计
Python 文件总数：71
总代码行数：14,376
```

---

## 📋 功能详情

### 安全检测规则

| 检测项 | 风险等级 | 说明 |
|--------|---------|------|
| 硬编码密码 | 🔴 严重 | 检测明文密码 |
| API Key 泄露 | 🟠 高危 | 检测 API 密钥 |
| eval/exec 使用 | 🟡 中危 | 检测危险函数 |
| 命令注入 | 🟡 中危 | 检测 os.system |
| SQL 注入 | 🟠 高危 | 检测 SQL 风险 |

### 审计报告

**JSON 格式**:
```json
{
  "timestamp": "2026-03-02T23:13:13",
  "security": {
    "critical": 0,
    "high": 0,
    "medium": 4,
    "low": 0
  },
  "code_quality": {...},
  "recommendations": [...]
}
```

**Markdown 格式**:
```markdown
# 紫微智控系统审计报告

## 系统概览
| 项目 | 数量 |
|------|------|
| 项目数 | 6 |
| Python 文件 | 71 |
```

---

## 🛠️ 高级用法

### 定时审计

```bash
# 每天凌晨 2 点执行
0 2 * * * python3 src/audit_ziwei_system.py
```

### 自定义检测规则

编辑 `src/audit_ziwei_system.py`:

```python
SECURITY_PATTERNS = {
    "hardcoded_password": (r'["\']PASSWORD["\']', "🔴 严重"),
    # 添加自定义规则...
}
```

### CI/CD 集成

```yaml
# GitHub Actions
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Audit
        run: python3 src/audit_ziwei_system.py
```

---

## 📊 审计指标

### 代码质量
- 平均每文件行数：100-300 行 ✅
- 函数密度：2-5 个/100 行 ✅
- 类密度：3-10 个/1000 行 ✅

### 安全指标
- 严重问题：0 ✅
- 高危问题：0 ✅
- 中危问题：<10 ⚠️

---

## 📄 文档

- [完整使用指南](docs/AUDIT_SYSTEM_README.md)
- [安全检测规则](docs/SECURITY_RULES.md)
- [最佳实践](docs/BEST_PRACTICES.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 更新日志

### v1.0.0 (2026-03-02)
- ✅ 初始版本发布
- ✅ 8 大审计功能
- ✅ JSON + Markdown 报告
- ✅ 安全检测规则
- ✅ 代码质量分析

---

## 📞 支持

- 📧 Email: pandac00@163.com
- 🐛 Issues: [GitHub Issues](https://github.com/ziwei-control/ziwei-audit-system/issues)
- 📚 文档：[完整文档](docs/AUDIT_SYSTEM_README.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🌟 统计

![Stars](https://img.shields.io/github/stars/ziwei-control/ziwei-audit-system?style=social)
![Forks](https://img.shields.io/github/forks/ziwei-control/ziwei-audit-system?style=social)
![Issues](https://img.shields.io/github/issues/ziwei-control/ziwei-audit-system)

---

**让代码更安全，让系统更可靠！** 🔒
