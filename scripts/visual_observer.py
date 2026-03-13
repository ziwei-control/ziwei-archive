#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 观察者视觉监控模块 v1.0
# 功能：观察者在观察时自动截取 Dashboard，视觉化监控系统状态
# =============================================================================

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入截图模块
from screenshot_module import (
    get_node_id,
    capture_dashboard,
    capture_screen,
    analyze_screenshot,
    log as screenshot_log
)

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
OBSERVER_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "visual_observer.log"
VISUAL_MEMORY = Ziwei_DIR / "data" / "knowledge" / "visual_memory.json"

# 确保目录存在
OBSERVER_LOG.parent.mkdir(parents=True, exist_ok=True)
VISUAL_MEMORY.parent.mkdir(parents=True, exist_ok=True)


def log(message: str):
    """记录观察者视觉日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [视觉] {message}\n"
    print(log_line.strip())
    with open(OBSERVER_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line)


class VisualObserver:
    """视觉观察者"""
    
    def __init__(self):
        self.node_id = None
        self.visual_memory = self.load_visual_memory()
        log("👁️ 视觉观察者初始化完成")
    
    def load_visual_memory(self) -> Dict:
        """加载视觉记忆"""
        if VISUAL_MEMORY.exists():
            with open(VISUAL_MEMORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'created': datetime.now().isoformat(),
            'screenshots': [],
            'patterns': [],
            'anomalies': []
        }
    
    def save_visual_memory(self):
        """保存视觉记忆"""
        self.visual_memory['updated'] = datetime.now().isoformat()
        with open(VISUAL_MEMORY, 'w', encoding='utf-8') as f:
            json.dump(self.visual_memory, f, indent=2, ensure_ascii=False)
        log(f"💾 视觉记忆已保存 ({len(self.visual_memory.get('screenshots', []))} 张截图)")
    
    def initialize_node(self) -> bool:
        """初始化 Node 设备"""
        log("🔧 尝试获取 Node 设备...")
        self.node_id = get_node_id("Ziwei")
        
        if self.node_id:
            log(f"✅ 找到 Node: {self.node_id}")
            return True
        else:
            log("❌ 未找到 Node 设备，请先运行：python3 screenshot_module.py setup")
            return False
    
    def observe_dashboard(self, save_to_memory: bool = True) -> Optional[Dict]:
        """
        观察 Dashboard（截取画面）
        
        Args:
            save_to_memory: 是否保存到视觉记忆
        
        Returns:
            观察结果字典
        """
        if not self.node_id:
            if not self.initialize_node():
                return None
        
        log("📸 开始观察 Dashboard...")
        
        # 截取画面
        image_path = capture_dashboard(self.node_id)
        
        if not image_path:
            log("❌ 截图失败")
            return None
        
        # 创建观察记录
        observation = {
            'timestamp': datetime.now().isoformat(),
            'type': 'dashboard',
            'image_path': image_path,
            'node_id': self.node_id,
            'status': 'captured',
            'analysis': None
        }
        
        # 分析画面
        log("🧠 分析画面内容...")
        analysis = analyze_screenshot(image_path, "Dashboard 系统监控画面")
        observation['analysis'] = analysis
        observation['status'] = 'analyzed'
        
        # 保存到视觉记忆
        if save_to_memory:
            self.visual_memory['screenshots'].append(observation)
            self.save_visual_memory()
        
        log(f"✅ Dashboard 观察完成：{image_path}")
        return observation
    
    def detect_anomalies(self, observation: Dict) -> List[str]:
        """
        检测异常（基于视觉分析）
        
        Args:
            observation: 观察结果
        
        Returns:
            异常列表
        """
        anomalies = []
        
        # TODO: 实现视觉异常检测
        # 例如：
        # - 检测错误提示（红色元素）
        # - 检测进程状态异常
        # - 检测数据异常（科学计数法余额等）
        
        log(f"🔍 异常检测完成，发现 {len(anomalies)} 个异常")
        return anomalies
    
    def compare_with_history(self, current: Dict, limit: int = 5) -> Dict:
        """
        与历史画面比较
        
        Args:
            current: 当前观察结果
            limit: 比较的历史记录数量
        
        Returns:
            比较结果
        """
        history = self.visual_memory.get('screenshots', [])[-limit:]
        
        comparison = {
            'current': current,
            'history_count': len(history),
            'changes': [],
            'patterns': []
        }
        
        # TODO: 实现视觉比较
        # 例如：
        # - 进程数量变化
        # - 数据格式变化
        # - 新增/消失的元素
        
        return comparison
    
    def periodic_observe(self, interval_minutes: int = 8):
        """
        定期观察
        
        Args:
            interval_minutes: 观察间隔（分钟）
        """
        log(f"⏰ 开始定期观察（每 {interval_minutes} 分钟）")
        
        # 这里应该由 cron 或定时器调用
        # 现在由观察者系统统一调度
        
        observation = self.observe_dashboard()
        
        if observation:
            anomalies = self.detect_anomalies(observation)
            
            if anomalies:
                log(f"⚠️ 发现 {len(anomalies)} 个异常，需要处理")
                # 可以触发告警或自动修复
        
        return observation
    
    def get_statistics(self) -> Dict:
        """获取视觉观察统计"""
        screenshots = self.visual_memory.get('screenshots', [])
        
        # 按类型统计
        by_type = {}
        for shot in screenshots:
            shot_type = shot.get('type', 'unknown')
            by_type[shot_type] = by_type.get(shot_type, 0) + 1
        
        # 按状态统计
        by_status = {}
        for shot in screenshots:
            status = shot.get('status', 'unknown')
            by_status[status] = by_status.get(status, 0) + 1
        
        # 最近观察时间
        last_observe = None
        if screenshots:
            last_observe = screenshots[-1].get('timestamp')
        
        return {
            'total_screenshots': len(screenshots),
            'by_type': by_type,
            'by_status': by_status,
            'last_observe': last_observe,
            'memory_file': str(VISUAL_MEMORY)
        }
    
    def cleanup_old_memories(self, days: int = 30):
        """
        清理旧视觉记忆
        
        Args:
            days: 保留天数
        """
        log(f"🧹 清理 {days} 天前的视觉记忆...")
        
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        original_count = len(self.visual_memory.get('screenshots', []))
        
        # 保留最近的截图
        self.visual_memory['screenshots'] = [
            shot for shot in self.visual_memory.get('screenshots', [])
            if shot.get('timestamp', '') > cutoff_str
        ]
        
        removed_count = original_count - len(self.visual_memory['screenshots'])
        
        self.save_visual_memory()
        
        log(f"✅ 清理完成，删除 {removed_count} 条旧记忆")


def status():
    """显示视觉观察者状态"""
    observer = VisualObserver()
    stats = observer.get_statistics()
    
    print("=" * 60)
    print("👁️ 紫微视觉观察者状态")
    print("=" * 60)
    print()
    print(f"📊 总截图数：{stats['total_screenshots']} 张")
    print()
    print("按类型统计:")
    for shot_type, count in stats.get('by_type', {}).items():
        print(f"  {shot_type}: {count} 张")
    print()
    print("按状态统计:")
    for status, count in stats.get('by_status', {}).items():
        print(f"  {status}: {count} 张")
    print()
    print(f"🕐 最后观察：{stats['last_observe'] or '从未'}")
    print()
    print(f"💾 记忆文件：{stats['memory_file']}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 visual_observer.py <command> [args]")
        print()
        print("命令:")
        print("  status          - 显示状态")
        print("  observe         - 观察 Dashboard")
        print("  init            - 初始化 Node")
        print("  cleanup [days]  - 清理旧记忆")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        status()
    
    elif command == "observe":
        observer = VisualObserver()
        observer.observe_dashboard()
    
    elif command == "init":
        observer = VisualObserver()
        observer.initialize_node()
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        observer = VisualObserver()
        observer.cleanup_old_memories(days)
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
