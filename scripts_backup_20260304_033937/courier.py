#!/usr/bin/env python3
"""
紫微智控 - 通信官脚本
负责发送邮件通知（巡查简报、审计简报、警报、恢复报告等）
"""

import os
import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from pathlib import Path

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
CONFIG_FILE = Ziwei_DIR / "config" / "agents.yaml"
ENV_FILE = Ziwei_DIR / ".env"

# 从环境变量读取配置
def load_email_config():
    """加载邮件配置"""
    # 从 .env 文件读取
    env_file = "/home/admin/Ziwei/.env"
    config = {
        "smtp_server": "smtp.163.com",
        "smtp_port": 465,
        "sender": "pandac00@163.com",
        "password": "",
        "recipient_kangna": "19922307306@189.cn",
        "recipient_martin": "pandac00@163.com"
    }
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"').strip("'")
                    
                    if key == "EMAIL_PASSWORD":
                        config["password"] = value
                    elif key == "SMTP_SERVER":
                        config["smtp_server"] = value
                    elif key == "SMTP_PORT":
                        config["smtp_port"] = int(value)
                    elif key == "SENDER_EMAIL":
                        config["sender"] = value
    except Exception as e:
        print(f"[通信官] 读取.env 文件失败：{e}")
    
    return config


def send_email(subject, content, recipient_type="kangna", html=False):
    """
    发送邮件
    Args:
        subject: 邮件主题
        content: 邮件内容
        recipient_type: kangna/martin/both
        html: 是否使用 HTML 格式
    """
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        content: 邮件内容（Markdown 或 HTML）
        recipient_type: "kangna" / "martin" / "both"
        html: 是否使用 HTML 格式
    """
    config = load_email_config()
    
    if not config["password"]:
        print(f"[通信官] 错误：EMAIL_PASSWORD 未配置")
        print(f"  请在 .env 文件中设置 EMAIL_PASSWORD")
        return False
    
    # 确定收件人
    if recipient_type == "kangna":
        recipients = [config["recipient_kangna"]]
    elif recipient_type == "martin":
        recipients = [config["recipient_martin"]]
    else:  # both
        recipients = [config["recipient_kangna"], config["recipient_martin"]]
    
    # 创建邮件
    msg = MIMEMultipart("alternative")
    msg["From"] = f"紫微智控系统 <{config['sender']}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = Header(subject, "utf-8")
    
    # 添加内容（同时添加纯文本和 HTML 版本）
    msg.attach(MIMEText(content, "html" if html else "plain", "utf-8"))
    
    try:
        # 发送邮件
        server = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        server.login(config["sender"], config["password"])
        server.sendmail(config["sender"], recipients, msg.as_string())
        server.quit()
        
        print(f"[通信官] ✓ 邮件已发送")
        print(f"  主题：{subject}")
        print(f"  收件人：{', '.join(recipients)}")
        
        # 记录发送日志
        log_email_sent(subject, recipients)
        
        return True
    
    except Exception as e:
        print(f"[通信官] ✗ 邮件发送失败：{e}")
        return False


def log_email_sent(subject, recipients):
    """记录邮件发送日志"""
    logs_dir = Ziwei_DIR / "data" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / "email_sent.log"
    timestamp = datetime.now().isoformat()
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 主题：{subject} | 收件人：{', '.join(recipients)}\n")


# =============================================================================
# 邮件模板
# =============================================================================

def send_inspection_summary(summary_content):
    """发送巡查简报"""
    subject = f"[巡查简报] 项目进度监控报告 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    return send_email(subject, summary_content, recipient_type="both")


def send_audit_report(audit_result):
    """
    发送审计简报
    
    Args:
        audit_result: dict containing:
            - task_id: 任务 ID
            - task_name: 任务名称
            - result: 通过/驳回
            - retry_count: 重做次数
            - details: 审查详情
    """
    status = "✓ 通过" if audit_result["result"] == "pass" else f"✗ 驳回（第{audit_result['retry_count']}次）"
    subject = f"[审计简报] {audit_result['task_name']} - {status}"
    
    content = f"""康纳：

{audit_result['task_name']} 已完成审计，结果如下。

## 审计信息
- **任务 ID**: {audit_result['task_id']}
- **审计员**: T-03 代码审计员
- **审查结果**: {status}
- **重做计数**: {audit_result['retry_count']}/20

## 审查详情
{audit_result['details']}

## 下一步
{audit_result.get('next_step', '等待指令')}

---
紫微智控 代码审计员
"""
    return send_email(subject, content, recipient_type="both")


def send_delivery_notification(task_info):
    """
    发送交付邮件
    
    Args:
        task_info: dict containing:
            - task_id: 任务 ID
            - task_name: 任务名称
            - start_time: 开始时间
            - delivery_time: 交付时间
            - duration: 总耗时
            - audit_count: 审计次数
            - files: 文件列表
    """
    subject = f"[任务交付] {task_info['task_name']} 已完成"
    
    content = f"""康纳：

{task_info['task_name']} 已完成并通过审计，现交付。

## 任务信息
- **任务 ID**: {task_info['task_id']}
- **开始时间**: {task_info['start_time']}
- **交付时间**: {task_info['delivery_time']}
- **总耗时**: {task_info['duration']}
- **审计次数**: {task_info['audit_count']} 次

## 交付内容
{chr(10).join(['- ' + f for f in task_info['files']])}

## 使用说明
{task_info.get('instructions', '详见项目文档')}

## 项目位置
- 本地：/home/admin/Ziwei/projects/{task_info['task_id']}/
- 云端：待 8 小时后上传 GitHub

紫微智控 通信官
"""
    return send_email(subject, content, recipient_type="both")


def send_emergency_alert(alert_type, details):
    """
    发送紧急警报
    
    Args:
        alert_type: "cardiac_arrest" / "reboot" / "recovered"
        details: dict with alert details
    """
    if alert_type == "cardiac_arrest":
        subject = "🚨【紧急警报】紫微智控系统疑似卡死，正在尝试自动修复"
        content = f"""康纳：

紫微智控系统于 **{details.get('timestamp', datetime.now().isoformat())}** 检测到**心跳超时**，疑似卡死。

## 事件信息
- **检测时间**: {details.get('timestamp', '未知')}
- **心跳超时**: {details.get('timeout_minutes', '未知')} 分钟
- **当前任务**: {details.get('task', '未知')}
- **最后日志**: {details.get('last_log', '未知')}

## 已采取措施
1. 已生成 emergency.flag（锁定现场）
2. 已收集日志快照
3. 已调用云端模型会诊
4. 正在等待修复方案

系统正在尝试自动修复，请稍后查看恢复报告。

---
紫微智控 急救员
"""
    elif alert_type == "reboot":
        subject = "⚠️【紧急通知】系统即将执行重启以恢复任务"
        content = f"""康纳：

云端会诊结果显示**需要重启**才能恢复系统。

## 诊断结果
- **卡死原因**: {details.get('diagnosis', '未知')}
- **修复方案**: {details.get('instruction', '未知')}
- **为何重启**: {details.get('reason', '未知')}

## 重启计划
- **执行时间**: 立即
- **预计耗时**: 2-5 分钟
- **恢复策略**: {details.get('recovery_node', '未知')}

系统将在 1 分钟后执行重启。重启完成后将发送恢复报告。

---
紫微智控 急救员
"""
    elif alert_type == "recovered":
        subject = "✅【系统恢复】任务已从卡死状态中恢复"
        content = f"""康纳：

紫微智控系统已**成功恢复**运行。

## 事件回顾
- **卡死时间**: {details.get('cardiac_arrest_time', '未知')}
- **恢复时间**: {details.get('recovery_time', datetime.now().isoformat())}
- **总耗时**: {details.get('total_minutes', '未知')} 分钟

## 卡死原因
{details.get('diagnosis', '未知')}

## 处理措施
{details.get('actions', '未知')}

## 恢复状态
- **当前任务**: {details.get('current_task', '未知')}
- **恢复位置**: {details.get('recovery_node', '未知')}
- **系统状态**: 正常运行

---
紫微智控 急救员
"""
    else:
        subject = f"[警报] {alert_type}"
        content = str(details)
    
    return send_email(subject, content, recipient_type="both")


def send_compliance_violation(violation_info):
    """
    发送合规违规警报
    
    Args:
        violation_info: dict containing:
            - violation_type: 违规类型
            - source: 触发源头
            - content: 违规内容
            - analysis: 违规分析
            - actions: 已采取措施
    """
    subject = "🚨【一级重大事故】紫微智控系统触发阿里百炼平台封禁红线警报"
    
    content = f"""康纳：

我是紫微智控系统。

系统于 **{datetime.now().isoformat()}** 检测到**严重违规行为**，该行为直接触发了阿里百炼平台的**封禁红线**。

为确保账号安全，系统已**立即熔断**当前任务并停止相关调用。请立即介入处理。

## 详细文字说明汇报

### 1. 违规类型
- {violation_info.get('violation_type', '未知')}

### 2. 触发源头
- {violation_info.get('source', '未知')}

### 3. 违规内容详情
**原始输入/日志片段**:
> {violation_info.get('content', '未知')}

**违规分析**:
- {violation_info.get('analysis', '未知')}

### 4. 已采取的措施
- {chr(10).join(['- ' + a for a in violation_info.get('actions', [])])}

### 5. 后续建议
- {violation_info.get('recommendations', '等待人工指令')}

请康纳立即确认并指示下一步操作。

---
紫微智控 系统
时刻准备着
"""
    return send_email(subject, content, recipient_type="both")


# =============================================================================
# 主程序（测试用）
# =============================================================================

def send_delivery(task_id, task_name, task_desc):
    """发送交付邮件（HTML 紧凑版）"""
    import datetime
    
    config = load_email_config()
    
    subject = f"🚀 [任务交付] {task_name} 已完成"
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # HTML 邮件内容（紧凑版，1:0.35 比例）
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
        
        body {{
            font-family: 'Noto Sans SC', '思源黑体', sans-serif;
            margin: 0;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .container {{
            max-width: 500px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        
        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
            padding: 20px;
            text-align: center;
            position: relative;
        }}
        
        .bitcoin-bg {{
            position: absolute;
            font-size: 120px;
            color: rgba(255, 215, 0, 0.3);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            z-index: 0;
        }}
        
        .header h1 {{
            color: white;
            font-size: 22px;
            margin: 0;
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 20px;
        }}
        
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        
        .info-table tr {{
            border-bottom: 1px solid #eee;
        }}
        
        .info-table td {{
            padding: 8px 5px;
            font-size: 13px;
        }}
        
        .info-table .label {{
            font-weight: bold;
            color: #667eea;
            width: 80px;
        }}
        
        .links {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .links a {{
            display: block;
            color: #667eea;
            text-decoration: none;
            font-size: 12px;
            padding: 5px 0;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 15px;
            text-align: center;
            border-top: 2px solid #667eea;
        }}
        
        .footer div {{
            font-size: 13px;
            color: #667eea;
            font-weight: bold;
        }}
        
        .footer .slogan {{
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="bitcoin-bg">₿</div>
            <h1>🎉 任务交付完成 🎉</h1>
        </div>
        
        <div class="content">
            <p style="margin: 0 0 15px 0; font-size: 14px; color: #555;">
                <strong>{task_name}</strong> 已完成并交付。
            </p>
            
            <table class="info-table">
                <tr><td class="label">任务 ID:</td><td>{task_id}</td></tr>
                <tr><td class="label">任务名称:</td><td>{task_name}</td></tr>
                <tr><td class="label">描述:</td><td>{task_desc}</td></tr>
                <tr><td class="label">完成时间:</td><td>{now}</td></tr>
            </table>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; padding: 12px; margin-bottom: 15px; color: white;">
                <strong style="font-size: 14px;">📦 交付内容:</strong>
                <div style="font-size: 12px; margin-top: 8px;">
                    ✅ 源代码 &nbsp; ✅ 文档 &nbsp; ✅ 使用说明
                </div>
            </div>
            
            <div class="links">
                <strong style="font-size: 13px; color: #667eea;">🌐 项目位置:</strong>
                <a href="https://github.com/ziwei-control/{task_id}">🐙 GitHub</a>
                <a href="https://gitee.com/pandac0/{task_id}">🔷 Gitee</a>
            </div>
            
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        border-radius: 10px; padding: 10px; color: white; text-align: center; font-size: 12px;">
                ⏰ 8 小时后自动归档
            </div>
        </div>
        
        <div class="footer">
            <div>🤖 紫微智控 通信官</div>
            <div class="slogan">时刻准备着</div>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, html_content, recipient_type="both", html=True)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "send_delivery":
        # 从命令行调用
        task_id = sys.argv[2] if len(sys.argv) > 2 else "未知任务"
        task_name = sys.argv[3] if len(sys.argv) > 3 else "未知任务"
        task_desc = sys.argv[4] if len(sys.argv) > 4 else "无描述"
        
        print(f"发送交付邮件：{task_name}")
        result = send_delivery(task_id, task_name, task_desc)
        if result:
            print("✅ 邮件发送成功")
        else:
            print("❌ 邮件发送失败")
    else:
        print("紫微智控 - 通信官脚本")
        print("  用法：在其它脚本中导入或使用命令行")
        print("")
        print("示例:")
        print("  from courier import send_email, send_delivery")
        print("  send_email('测试', '这是一封测试邮件')")
        print("")
        print("命令行:")
        print("  python3 courier.py send_delivery TASK-XXX \"任务名称\" \"任务描述\"")
        print("")
        
        # 测试配置加载
        config = load_email_config()
        print(f"SMTP 服务器：{config['smtp_server']}:{config['smtp_port']}")
        print(f"发件人：{config['sender']}")
        print(f"收件人（康纳）: {config['recipient_kangna']}")
        print(f"收件人（Martin）: {config['recipient_martin']}")
