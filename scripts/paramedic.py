#!/usr/bin/env python3
"""
紫微智控 - 急救员监控脚本
负责心跳监控、云端会诊、重启恢复
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
Ziwei_DIR = Path("/home/admin/Ziwei")
HEALTH_DIR = Ziwei_DIR / "data" / "health"
LOGS_DIR = Ziwei_DIR / "data" / "logs"
CONFIG_FILE = Ziwei_DIR / "config" / "agents.yaml"

# 文件路径
HEARTBEAT_FILE = HEALTH_DIR / "heartbeat.log"
EMERGENCY_FLAG = HEALTH_DIR / "emergency.flag"
RECOVERY_PLAN = HEALTH_DIR / "recovery_plan.txt"

# API 配置（从环境变量读取）
BAILIAN_API_KEY = os.getenv("BAILIAN_API_KEY", "")
BAILIAN_URL = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"

# 阈值配置
HEARTBEAT_INTERVAL = 30  # 秒
HEARTBEAT_TIMEOUT = 2    # 分钟


def check_heartbeat():
    """检查心跳文件"""
    if not HEARTBEAT_FILE.exists():
        return False, "心跳文件不存在"
    
    mtime = datetime.fromtimestamp(HEARTBEAT_FILE.stat().st_mtime)
    elapsed = datetime.now() - mtime
    
    if elapsed > timedelta(minutes=HEARTBEAT_TIMEOUT):
        return False, f"心跳超时 {elapsed.seconds // 60} 分钟"
    
    return True, f"正常 (上次更新：{mtime.strftime('%H:%M:%S')})"


def collect_logs():
    """收集日志快照"""
    logs = {
        "heartbeat": [],
        "recent_tasks": [],
        "system_status": ""
    }
    
    # 读取心跳日志（最近 20 行）
    if HEARTBEAT_FILE.exists():
        with open(HEARTBEAT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            logs["heartbeat"] = lines[-20:]
    
    # 读取系统状态
    status_file = Ziwei_DIR / "data" / "system_status.md"
    if status_file.exists():
        with open(status_file, "r", encoding="utf-8") as f:
            logs["system_status"] = f.read()
    
    return logs


def cloud_consultation(logs):
    """调用云端模型会诊"""
    if not BAILIAN_API_KEY:
        print("[急救员] 警告：BAILIAN_API_KEY 未配置，使用默认方案")
        return {
            "diagnosis": "API Key 未配置，无法云端会诊",
            "instruction": "检查 .env 文件配置",
            "recovery_node": "从系统监控继续",
            "requires_reboot": False
        }
    
    prompt = f"""你是紫微智控的首席技术官，正在参与一场紧急会诊。

我们的急救员系统检测到本地调度主机可能已因任务阻塞而卡死。

你的任务是基于提供的日志快照，进行远程诊断，并给出具体的、可操作的恢复指令。

请注意：
- 执行端（本地主机）资源极其有限（2G 内存），只能执行简单的文件操作或指令修改
- 严禁建议本地复杂计算或人工干预
- 输出必须是 JSON 格式，便于脚本解析执行

请严格按照以下步骤分析：
1. 诊断病因（死循环/资源阻塞/逻辑死锁/数据异常）
2. 开具处方（终止任务/跳过步骤/调整参数/切换备用）
3. 输出 JSON 格式的诊断结果和指令

日志快照：
心跳日志：
{"".join(logs['heartbeat'])}

系统状态：
{logs['system_status']}

请输出 JSON 格式（不要 Markdown）：
{{
  "diagnosis": "一句话描述卡死原因",
  "instruction": "具体可执行的操作指令",
  "recovery_node": "建议恢复执行的断点位置",
  "requires_reboot": false
}}
"""
    
    try:
        headers = {
            "Authorization": f"Bearer {BAILIAN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen3.5-plus",
            "messages": [
                {
                    "role": "system",
                    "content": "你是紫微智控的 CTO，负责紧急故障诊断。请输出纯 JSON，不要 Markdown 格式。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }
        
        response = requests.post(BAILIAN_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # 解析 JSON（可能包含 Markdown 代码块）
        content = content.replace("```json", "").replace("```", "").strip()
        diagnosis = json.loads(content)
        
        print(f"[急救员] 云端会诊完成")
        print(f"  诊断：{diagnosis.get('diagnosis', '未知')}")
        print(f"  指令：{diagnosis.get('instruction', '无')}")
        print(f"  重启：{'是' if diagnosis.get('requires_reboot') else '否'}")
        
        return diagnosis
    
    except Exception as e:
        print(f"[急救员] 云端会诊失败：{e}")
        return {
            "diagnosis": f"云端会诊失败：{e}",
            "instruction": "手动检查系统状态",
            "recovery_node": "从心跳监控继续",
            "requires_reboot": False
        }


def execute_recovery(diagnosis):
    """执行恢复方案"""
    instruction = diagnosis.get("instruction", "")
    requires_reboot = diagnosis.get("requires_reboot", False)
    
    print(f"[急救员] 执行恢复方案...")
    
    # 简单指令执行（仅限安全操作）
    if "删除" in instruction and "task" in instruction.lower():
        print(f"[急救员] 执行：{instruction}")
        # TODO: 实现安全的文件删除逻辑
    
    if requires_reboot:
        print(f"[急救员] 需要重启，保存恢复计划...")
        save_recovery_plan(diagnosis)
        # TODO: 执行重启（需要权限）
        # os.system("sudo reboot")
    
    return True


def save_recovery_plan(diagnosis):
    """保存恢复计划"""
    with open(RECOVERY_PLAN, "w", encoding="utf-8") as f:
        f.write(f"诊断：{diagnosis.get('diagnosis', '')}\n")
        f.write(f"指令：{diagnosis.get('instruction', '')}\n")
        f.write(f"恢复位置：{diagnosis.get('recovery_node', '')}\n")
        f.write(f"需要重启：{diagnosis.get('requires_reboot', False)}\n")
    print(f"[急救员] 恢复计划已保存：{RECOVERY_PLAN}")


def send_alert_email(subject, content):
    """发送警报邮件（待实现）"""
    # TODO: 调用通信官发送邮件
    print(f"[急救员] 邮件警报：{subject}")
    print(f"  {content[:200]}...")


def trigger_emergency(reason):
    """触发应急响应"""
    print(f"\n{'='*60}")
    print(f"[急救员] 🚨 触发应急响应")
    print(f"  原因：{reason}")
    print(f"  时间：{datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # 1. 生成 emergency.flag
    EMERGENCY_FLAG.touch()
    print(f"[急救员] 已生成 emergency.flag")
    
    # 2. 收集日志快照
    logs = collect_logs()
    print(f"[急救员] 已收集日志快照")
    
    # 3. 云端会诊
    diagnosis = cloud_consultation(logs)
    
    # 4. 发送第一封邮件：卡死警报
    send_alert_email(
        "🚨【紧急警报】紫微智控系统疑似卡死，正在尝试自动修复",
        f"系统于 {datetime.now().isoformat()} 检测到心跳超时：{reason}\n\n诊断结果：{diagnosis.get('diagnosis', '未知')}"
    )
    
    # 5. 判断是否需要重启
    if diagnosis.get("requires_reboot"):
        # 发送第二封邮件：重启通知
        send_alert_email(
            "⚠️【紧急通知】系统即将执行重启以恢复任务",
            f"云端会诊结果显示需要重启。\n\n诊断：{diagnosis.get('diagnosis', '未知')}\n恢复策略：{diagnosis.get('recovery_node', '未知')}"
        )
        
        # 保存恢复计划
        save_recovery_plan(diagnosis)
        
        # TODO: 执行重启
        print(f"[急救员] 准备重启系统...")
        # os.system("sudo reboot")
    else:
        # 执行恢复方案
        execute_recovery(diagnosis)
    
    # 6. 发送第三封邮件：恢复报告（重启后）
    # TODO: 在 startup.sh 中检测并发送


def main():
    """主循环"""
    print(f"{'='*60}")
    print(f"紫微智控 - 急救员监控启动")
    print(f"  心跳检测：每 {HEARTBEAT_INTERVAL} 秒")
    print(f"  超时阈值：{HEARTBEAT_TIMEOUT} 分钟")
    print(f"  工作目录：{Ziwei_DIR}")
    print(f"{'='*60}\n")
    
    last_check = time.time()
    
    try:
        while True:
            healthy, message = check_heartbeat()
            
            if healthy:
                print(f"[{datetime.now().isoformat()}] ✓ {message}")
            else:
                print(f"[{datetime.now().isoformat()}] ✗ {message}")
                trigger_emergency(message)
            
            last_check = time.time()
            time.sleep(HEARTBEAT_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n[急救员] 收到停止信号，正常退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n[急救员] 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
