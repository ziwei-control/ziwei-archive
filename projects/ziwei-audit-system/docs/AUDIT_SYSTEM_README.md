# 🔍 紫微智控 - 自动化审计系统

## 📋 系统概述

紫微智控审计系统是一套**全面、自动化、可定制**的代码和安全审计工具，专门用于监控和评估整个紫微智控系统的健康状态、安全性和代码质量。

---

## 🎯 核心功能

### 1. 项目结构审计
- ✅ 自动扫描所有项目目录
- ✅ 统计文件数量、类型、大小
- ✅ 识别 Python 文件占比
- ✅ 生成项目清单

### 2. 运行服务审计
- ✅ 检测正在运行的服务进程
- ✅ 识别服务 PID
- ✅ 标记未运行的服务
- ✅ 支持自定义服务列表

### 3. 安全审计
- ✅ 硬编码密码检测
- ✅ API Key 泄露检测
- ✅ eval/exec 使用检测
- ✅ 命令注入风险检测
- ✅ SQL 注入风险检测
- ✅ 风险等级分类（严重/高/中/低）

### 4. 代码质量审计
- ✅ 代码行数统计
- ✅ 函数数量统计
- ✅ 类数量统计
- ✅ 平均代码规模分析
- ✅ 文档字符串统计

### 5. 配置文件审计
- ✅ .env 文件检测
- ✅ 权限检查（600/644/777）
- ✅ .gitignore 配置检查
- ✅ config.yaml/json 检查

### 6. Git 仓库审计
- ✅ 自动识别 Git 仓库
- ✅ 仓库列表生成
- ✅ 远程仓库配置检查

### 7. 磁盘使用审计
- ✅ 总大小计算
- ✅ 排除.git 目录
- ✅ 空间使用分析

### 8. 审计报告生成
- ✅ JSON 格式报告
- ✅ Markdown 格式报告
- ✅ 时间戳记录
- ✅ 历史报告保存

---

## 📁 文件结构

```
/home/admin/Ziwei/
├── audit_ziwei_system.py          # 主审计脚本
├── audits/                        # 审计报告目录
│   ├── audit_report_YYYYMMDD_HHMMSS.json
│   └── audit_report_YYYYMMDD_HHMMSS.md
└── docs/
    └── AUDIT_SYSTEM_README.md     # 本文档
```

---

## 🚀 使用方法

### 快速启动

```bash
# 运行审计
python3 /home/admin/Ziwei/audit_ziwei_system.py
```

### 输出示例

```
======================================================================
🔍 紫微智控系统 - 全面审计
======================================================================
📅 审计时间：2026-03-02 23:13:13
📂 审计目录：/home/admin/Ziwei

======================================================================
📁 项目结构审计
======================================================================

✅ x402-api                  | 文件：  32 | Python:  20 | 大小：   111.4 KB
✅ x402-python-sdk           | 文件：  16 | Python:   8 | 大小：    35.1 KB
...
```

---

## 🔧 配置说明

### 审计目标配置

编辑脚本中的 `projects` 字典：

```python
projects = {
    "x402-api": "/home/admin/Ziwei/projects/x402-api",
    "x402-python-sdk": "/home/admin/Ziwei/projects/x402-python-sdk",
    "x402-trading-bot": "/home/admin/Ziwei/projects/x402-trading-bot",
    "global-warroom": "/home/admin/Ziwei/projects/global-warroom",
    "global-warroom-upgraded": "/home/admin/Ziwei/projects/global-warroom-upgraded",
    "scripts": "/home/admin/Ziwei/scripts"
}
```

### 安全检测模式

编辑 `SECURITY_PATTERNS` 字典：

```python
SECURITY_PATTERNS = {
    "hardcoded_password": (r'["\']PASSWORD["\']', "🔴 严重"),
    "hardcoded_api_key": (r'api_key\s*=\s*["\'][a-zA-Z0-9]{20,}', "🟠 高"),
    "eval_exec": (r'\b(eval|exec)\s*\(', "🟡 中"),
    # 添加自定义模式...
}
```

### 运行服务检测

编辑 `services_to_check` 列表：

```python
services_to_check = [
    ("x402 API", "app_production.py"),
    ("全球战情室", "warroom"),
    ("交易机器人", "bot_production")
]
```

---

## 📊 审计报告

### JSON 报告示例

```json
{
  "timestamp": "2026-03-02T23:13:13",
  "projects": {
    "x402-api": {
      "path": "/home/admin/Ziwei/projects/x402-api",
      "total_files": 32,
      "python_files": 20,
      "total_size_kb": 111.4
    }
  },
  "security": {
    "critical": 0,
    "high": 0,
    "medium": 4,
    "low": 0
  },
  "code_quality": {
    "total_python_files": 71,
    "total_lines": 14376,
    "total_functions": 422,
    "total_classes": 47
  },
  "running_services": [...],
  "recommendations": [...]
}
```

### Markdown 报告示例

```markdown
# 紫微智控系统审计报告

**审计时间**: 2026-03-02 23:13:13

## 系统概览

| 项目 | 数量 |
|------|------|
| 项目数 | 6 |
| Python 文件 | 71 |
| 代码行数 | 14,376 |
| 运行服务 | 1 |

## 安全状态

| 级别 | 数量 |
|------|------|
| 严重 | 0 |
| 高危 | 0 |
| 中危 | 4 |
| 低危 | 0 |
```

---

## 🔍 安全检测规则

### 1. 硬编码密码检测

**模式**: `["\']UMayTeWFZsFqwv6M["\']`

**风险等级**: 🔴 严重

**示例**:
```python
# ❌ 错误
password = "UMayTeWFZsFqwv6M"

# ✅ 正确
password = os.getenv("SENDER_PASSWORD")
```

### 2. API Key 检测

**模式**: `api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']`

**风险等级**: 🟠 高

**示例**:
```python
# ❌ 错误
API_KEY = "sk-sp-deb52dabf75c47308911359d51a0a420"

# ✅ 正确
API_KEY = os.getenv("DASHSCOPE_API_KEY")
```

### 3. eval/exec 检测

**模式**: `\b(eval|exec)\s*\(`

**风险等级**: 🟡 中

**示例**:
```python
# ❌ 错误
result = eval(user_input)

# ✅ 正确
import ast
result = ast.literal_eval(user_input)
```

### 4. 命令注入检测

**模式**: `os\.system\s*\(|subprocess\.call\s*\(`

**风险等级**: 🟡 中

**示例**:
```python
# ❌ 错误
os.system(f"rm -rf {user_input}")

# ✅ 正确
subprocess.run(['rm', '-rf', sanitized_path])
```

---

## 📈 审计指标

### 代码质量指标

| 指标 | 说明 | 健康范围 |
|------|------|---------|
| 平均每文件行数 | 代码模块化程度 | 100-300 行 |
| 函数密度 | 每 100 行函数数量 | 2-5 个 |
| 类密度 | 每 1000 行类数量 | 3-10 个 |
| 文档字符串比例 | 有文档的函数占比 | >50% |

### 安全指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 严重问题数 | 硬编码密码等 | 0 |
| 高危问题数 | API Key 泄露等 | 0 |
| 中危问题数 | eval/exec 使用 | <10 |
| 低危问题数 | 代码规范问题 | <50 |

### 运行指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 服务运行数 | 正常运行的服务 | 全部 |
| 配置正确率 | .env 权限 600 比例 | 100% |
| Git 提交频率 | 最近 7 天提交数 | >5 次 |

---

## 🛠️ 高级用法

### 定时审计

```bash
# 每天凌晨 2 点执行审计
0 2 * * * python3 /home/admin/Ziwei/audit_ziwei_system.py >> /home/admin/Ziwei/audits/cron.log 2>&1
```

### 对比历史报告

```python
import json

# 加载两份报告
with open('audit_report_1.json') as f:
    report1 = json.load(f)

with open('audit_report_2.json') as f:
    report2 = json.load(f)

# 对比安全问题变化
print(f"安全问题变化：{report1['security']['critical']} → {report2['security']['critical']}")
```

### 自定义报告格式

```python
# 在脚本末尾添加自定义报告生成
def generate_custom_report(results):
    html = f"""
    <html>
    <h1>审计报告</h1>
    <p>安全问题：{results['security']['critical']}</p>
    </html>
    """
    with open('report.html', 'w') as f:
        f.write(html)
```

---

## 📋 最佳实践

### 1. 定期审计

```bash
# 每周一次全面审计
0 9 * * 1 python3 /home/admin/Ziwei/audit_ziwei_system.py
```

### 2. 提交前审计

```bash
# Git pre-commit hook
#!/bin/bash
python3 /home/admin/Ziwei/audit_ziwei_system.py
if [ $? -ne 0 ]; then
    echo "审计未通过，请修复问题"
    exit 1
fi
```

### 3. 持续集成

```yaml
# .github/workflows/audit.yml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Audit
        run: python3 audit_ziwei_system.py
```

---

## 🔧 故障排查

### 问题 1: 审计脚本无法运行

```bash
# 检查 Python 版本
python3 --version  # 需要 3.6+

# 检查权限
chmod +x /home/admin/Ziwei/audit_ziwei_system.py
```

### 问题 2: 报告无法生成

```bash
# 检查目录是否存在
mkdir -p /home/admin/Ziwei/audits

# 检查磁盘空间
df -h /home/admin/Ziwei
```

### 问题 3: 误报安全问题

编辑 `SECURITY_PATTERNS` 调整检测规则：

```python
# 降低某个规则的敏感度
"eval_exec": (r'^\s*eval\s*\(', "🟡 中"),  # 仅检测行首的 eval
```

---

## 📞 技术支持

### 查看审计日志

```bash
tail -100 /home/admin/Ziwei/audits/cron.log
```

### 导出审计数据

```bash
# 导出所有报告
cp /home/admin/Ziwei/audits/*.json /backup/audits/
```

### 分享审计报告

```bash
# 生成最新报告
latest_report=$(ls -t /home/admin/Ziwei/audits/*.md | head -1)

# 发送邮件
mail -s "审计报告" user@example.com < $latest_report
```

---

## 🎯 未来规划

### 功能扩展

- [ ] Web 界面展示
- [ ] 实时告警系统
- [ ] 自动修复建议
- [ ] 趋势分析图表
- [ ] 多项目对比

### 集成扩展

- [ ] GitHub Actions 集成
- [ ] GitLab CI 集成
- [ ] Slack 通知
- [ ] 邮件报告
- [ ] API 接口

---

## 📄 许可证

MIT License

---

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2026-03-02
**版本**: 1.0.0
**作者**: 紫微智控团队
