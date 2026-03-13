#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 屏幕截图模块 v1.0
# 功能：自动截取 Dashboard 和系统画面，用于观察者视觉监控
# =============================================================================

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
SCREENSHOT_DIR = Ziwei_DIR / "data" / "screenshots"
LOG_FILE = Ziwei_DIR / "data" / "logs" / "observer" / "screenshot.log"
GATEWAY_TOKEN = "73c8f5efc97f05b131130f5dc069b2aaee15d28761ddac2c"
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = "18789"

# 确保目录存在
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)


def setup_node(display_name: str = "Ziwei Server Node") -> Optional[str]:
    """
    设置 Node 设备
    
    Returns:
        node_id: Node 设备 ID，失败返回 None
    """
    log(f"🔧 开始设置 Node 设备：{display_name}")
    
    # 检查 Node 是否已运行
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['OPENCLAW_GATEWAY_TOKEN'] = GATEWAY_TOKEN
        
        # 启动 Node（后台运行）
        node_cmd = [
            'openclaw', 'node', 'run',
            '--host', GATEWAY_HOST,
            '--port', GATEWAY_PORT,
            '--display-name', display_name
        ]
        
        log(f"启动 Node: {' '.join(node_cmd)}")
        # 注意：这里只是示例，实际需要在系统服务中运行
        # subprocess.Popen(node_cmd, env=env)
        
        log("✅ Node 启动说明已记录，请手动执行以下命令：")
        log(f"  openclaw node run --host {GATEWAY_HOST} --port {GATEWAY_PORT} --display-name \"{display_name}\"")
        
        return None
        
    except Exception as e:
        log(f"❌ Node 设置失败：{e}")
        return None


def approve_node(request_id: str) -> bool:
    """
    批准 Node 配对
    
    Args:
        request_id: 配对请求 ID
    
    Returns:
        成功返回 True
    """
    try:
        log(f"批准 Node 配对：{request_id}")
        subprocess.run(['openclaw', 'devices', 'approve', request_id], check=True)
        log("✅ Node 配对成功")
        return True
    except Exception as e:
        log(f"❌ 配对失败：{e}")
        return False


def get_node_id(node_name: str = "Ziwei") -> Optional[str]:
    """
    获取 Node 设备 ID
    
    Args:
        node_name: Node 名称
    
    Returns:
        node_id: Node 设备 ID
    """
    try:
        env = os.environ.copy()
        env['OPENCLAW_GATEWAY_TOKEN'] = GATEWAY_TOKEN
        
        result = subprocess.run(
            ['openclaw', 'nodes', 'status'],
            env=env,
            capture_output=True,
            text=True
        )
        
        # 解析输出查找 Node ID
        for line in result.stdout.split('\n'):
            if node_name in line:
                # 提取 Node ID
                parts = line.split()
                if parts:
                    node_id = parts[0]
                    log(f"找到 Node: {node_id}")
                    return node_id
        
        log("⚠️ 未找到 Node 设备")
        return None
        
    except Exception as e:
        log(f"❌ 获取 Node ID 失败：{e}")
        return None


def capture_dashboard(node_id: str, format: str = "png") -> Optional[str]:
    """
    截取 Dashboard 画面
    
    Args:
        node_id: Node 设备 ID
        format: 图片格式 (png/jpg)
    
    Returns:
        图片路径，失败返回 None
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = SCREENSHOT_DIR / f"dashboard_{timestamp}.{format}"
        
        env = os.environ.copy()
        env['OPENCLAW_GATEWAY_TOKEN'] = GATEWAY_TOKEN
        
        log(f"📸 截取 Dashboard 画面...")
        
        result = subprocess.run(
            [
                'openclaw', 'nodes', 'canvas', 'snapshot',
                '--node', node_id,
                '--format', format
            ],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and 'MEDIA:' in result.stdout:
            # 提取 MEDIA 路径
            media_path = result.stdout.strip().split('MEDIA:')[1].split()[0]
            log(f"✅ 截图成功：{media_path}")
            
            # 复制到保存目录
            import shutil
            if Path(media_path).exists():
                shutil.copy(media_path, output_file)
                log(f"💾 已保存到：{output_file}")
                return str(output_file)
        
        log(f"❌ 截图失败：{result.stderr}")
        return None
        
    except Exception as e:
        log(f"❌ 截图异常：{e}")
        return None


def capture_screen(node_id: str, duration: str = "5s", fps: int = 10) -> Optional[str]:
    """
    录制屏幕视频
    
    Args:
        node_id: Node 设备 ID
        duration: 录制时长 (如 "5s", "10s")
        fps: 帧率
    
    Returns:
        视频路径，失败返回 None
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = SCREENSHOT_DIR / f"screen_{timestamp}.mp4"
        
        env = os.environ.copy()
        env['OPENCLAW_GATEWAY_TOKEN'] = GATEWAY_TOKEN
        
        log(f"🎥 录制屏幕视频 ({duration}, {fps}fps)...")
        
        result = subprocess.run(
            [
                'openclaw', 'nodes', 'screen', 'record',
                '--node', node_id,
                '--duration', duration,
                '--fps', str(fps)
            ],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and 'MEDIA:' in result.stdout:
            media_path = result.stdout.strip().split('MEDIA:')[1].split()[0]
            log(f"✅ 录制成功：{media_path}")
            
            import shutil
            if Path(media_path).exists():
                shutil.copy(media_path, output_file)
                log(f"💾 已保存到：{output_file}")
                return str(output_file)
        
        log(f"❌ 录制失败：{result.stderr}")
        return None
        
    except Exception as e:
        log(f"❌ 录制异常：{e}")
        return None


def analyze_screenshot(image_path: str, description: str = "") -> Dict:
    """
    分析截图内容（使用 AI 视觉模型）
    
    Args:
        image_path: 图片路径
        description: 分析描述
    
    Returns:
        分析结果字典
    """
    try:
        log(f"🧠 分析截图：{image_path}")
        
        # 这里可以调用 AI 视觉模型分析图片
        # 例如使用 Qwen Vision 模型
        
        result = {
            'image_path': image_path,
            'analyzed_at': datetime.now().isoformat(),
            'description': description,
            'status': 'pending',  # pending/analyzed/failed
            'analysis': None
        }
        
        log("✅ 分析任务已创建")
        return result
        
    except Exception as e:
        log(f"❌ 分析失败：{e}")
        return {
            'image_path': image_path,
            'analyzed_at': datetime.now().isoformat(),
            'status': 'failed',
            'error': str(e)
        }


def cleanup_old_screenshots(days: int = 7):
    """
    清理旧截图
    
    Args:
        days: 保留天数
    """
    try:
        log(f"🧹 清理 {days} 天前的截图...")
        
        import time
        now = time.time()
        cutoff = now - (days * 86400)
        
        for file in SCREENSHOT_DIR.glob('*'):
            if file.stat().st_mtime < cutoff:
                file.unlink()
                log(f"删除：{file.name}")
        
        log("✅ 清理完成")
        
    except Exception as e:
        log(f"❌ 清理失败：{e}")


def status():
    """显示截图模块状态"""
    print("=" * 60)
    print("📸 紫微截图模块状态")
    print("=" * 60)
    print()
    
    # 截图目录
    screenshot_count = len(list(SCREENSHOT_DIR.glob('*')))
    total_size = sum(f.stat().st_size for f in SCREENSHOT_DIR.glob('*'))
    print(f"📁 截图目录：{SCREENSHOT_DIR}")
    print(f"📊 截图数量：{screenshot_count} 个")
    print(f"💾 总大小：{total_size / 1024 / 1024:.2f} MB")
    print()
    
    # 日志文件
    if LOG_FILE.exists():
        log_lines = sum(1 for _ in open(LOG_FILE))
        print(f"📝 日志文件：{LOG_FILE}")
        print(f"📊 日志行数：{log_lines} 行")
    print()
    
    # Node 状态
    env = os.environ.copy()
    env['OPENCLAW_GATEWAY_TOKEN'] = GATEWAY_TOKEN
    result = subprocess.run(
        ['openclaw', 'nodes', 'status'],
        env=env,
        capture_output=True,
        text=True
    )
    print("🖥️ Node 状态:")
    print(result.stdout)
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 screenshot_module.py <command> [args]")
        print()
        print("命令:")
        print("  status              - 显示状态")
        print("  setup [name]        - 设置 Node")
        print("  approve <requestId> - 批准配对")
        print("  capture [node_id]   - 截取 Dashboard")
        print("  record [node_id]    - 录制屏幕")
        print("  cleanup [days]      - 清理旧截图")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        status()
    
    elif command == "setup":
        name = sys.argv[2] if len(sys.argv) > 2 else "Ziwei Server Node"
        setup_node(name)
    
    elif command == "approve":
        if len(sys.argv) < 3:
            print("❌ 需要提供 request_id")
            sys.exit(1)
        approve_node(sys.argv[2])
    
    elif command == "capture":
        node_id = sys.argv[2] if len(sys.argv) > 2 else get_node_id()
        if node_id:
            capture_dashboard(node_id)
        else:
            print("❌ 未指定 Node ID 且未找到默认 Node")
    
    elif command == "record":
        node_id = sys.argv[2] if len(sys.argv) > 2 else get_node_id()
        if node_id:
            capture_screen(node_id)
        else:
            print("❌ 未指定 Node ID 且未找到默认 Node")
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        cleanup_old_screenshots(days)
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
