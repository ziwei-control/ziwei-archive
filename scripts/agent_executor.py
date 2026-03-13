#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - Agent 任务执行器
# 功能：执行观察者分配给三个 agent（爱人、信念、如意）的任务
# =============================================================================

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
TASK_QUEUE = Ziwei_DIR / "data" / "strategy" / "observer_tasks.json"
AGENT_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "agent_execution.log"
KNOWLEDGE_BASE = Ziwei_DIR / "data" / "knowledge" / "work_methodology.json"

# 确保目录存在
AGENT_LOG.parent.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE.parent.mkdir(parents=True, exist_ok=True)

# 导入学习模块
sys.path.insert(0, str(Ziwei_DIR / "scripts"))
try:
    from observer_learning import ObserverLearner
    LEARNER = ObserverLearner()
except Exception as e:
    print(f"⚠️  学习模块加载失败：{e}")
    LEARNER = None


class AgentExecutor:
    """Agent 任务执行器"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.tasks_completed = 0
        
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{self.agent_name}] {message}\n"
        
        with open(AGENT_LOG, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        print(log_line, end='')
    
    def load_tasks(self) -> dict:
        """加载任务队列"""
        if not TASK_QUEUE.exists():
            self.log("ℹ️  任务队列为空")
            return {'tasks': {self.agent_name: []}}
        
        try:
            with open(TASK_QUEUE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"❌ 读取任务队列失败：{e}")
            return {'tasks': {self.agent_name: []}}
    
    def execute_task(self, task: dict) -> bool:
        """执行单个任务"""
        issue = task.get('issue', '未知问题')
        suggestion = task.get('suggestion', '无建议')
        component = task.get('component', '未知组件')
        
        self.log(f"📋 执行任务：{issue}")
        self.log(f"   建议：{suggestion}")
        
        try:
            # 根据组件和建议执行相应操作
            if '策略引擎' in component and '重复' in issue:
                return self.fix_duplicate_processes()
            
            elif '策略引擎' in component and '未运行' in issue:
                return self.start_strategy_engine()
            
            elif '交易数据' in component and '异常' in issue:
                return self.clean_abnormal_trades()
            
            elif '磁盘' in component or '空间' in component:
                return self.clean_disk_space()
            
            elif 'Dashboard' in component:
                return self.fix_dashboard()
            
            elif 'Supervisor' in component:
                return self.fix_supervisor()
            
            elif '进程' in suggestion or '清理' in suggestion:
                return self.fix_duplicate_processes()
            
            else:
                self.log(f"⚠️  未知任务类型，需要人工干预")
                return False
                
        except Exception as e:
            self.log(f"❌ 执行失败：{e}")
            return False
    
    def fix_duplicate_processes(self) -> bool:
        """修复重复进程"""
        self.log("🔧 清理重复的策略引擎进程...")
        
        # 停止所有策略引擎进程
        subprocess.run("pkill -f 'strategy_engine_v3'", shell=True)
        subprocess.run("pkill -f 'soul_trader'", shell=True)
        
        import time
        time.sleep(2)
        
        # 启动单个进程
        subprocess.Popen(
            "cd /home/admin/Ziwei/projects/x402-trading-bot && "
            "nohup python3 strategy_engine_v3.py > "
            "/home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log 2>&1 &",
            shell=True
        )
        
        self.log("✅ 重复进程已清理")
        return True
    
    def start_strategy_engine(self) -> bool:
        """启动策略引擎"""
        self.log("🚀 启动策略引擎...")
        
        subprocess.Popen(
            "cd /home/admin/Ziwei/projects/x402-trading-bot && "
            "nohup python3 strategy_engine_v3.py > "
            "/home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log 2>&1 &",
            shell=True
        )
        
        self.log("✅ 策略引擎已启动")
        return True
    
    def clean_abnormal_trades(self) -> bool:
        """清理异常交易数据"""
        self.log("🧹 清理异常交易数据...")
        
        trade_file = Ziwei_DIR / "data" / "strategy" / "trade_history.jsonl"
        
        if not trade_file.exists():
            self.log("⚠️  交易历史文件不存在")
            return False
        
        try:
            with open(trade_file, 'r', encoding='utf-8') as f:
                trades = [json.loads(line) for line in f if line.strip()]
            
            # 过滤正常交易
            clean_trades = [t for t in trades if t.get('value', 0) >= 1.0]
            
            # 保存清理后的数据
            with open(trade_file, 'w', encoding='utf-8') as f:
                for t in clean_trades:
                    f.write(json.dumps(t) + '\n')
            
            removed = len(trades) - len(clean_trades)
            self.log(f"✅ 清理了 {removed} 笔异常交易")
            return True
            
        except Exception as e:
            self.log(f"❌ 清理失败：{e}")
            return False
    
    def clean_disk_space(self) -> bool:
        """清理磁盘空间"""
        self.log("🧹 清理磁盘空间...")
        
        # 清理旧日志
        log_dir = Ziwei_DIR / "data" / "logs"
        
        import glob
        old_logs = glob.glob(str(log_dir / "*.log.*"))
        
        for log_file in old_logs[:10]:  # 最多清理 10 个旧日志
            try:
                os.remove(log_file)
                self.log(f"  删除：{log_file}")
            except:
                pass
        
        self.log("✅ 磁盘空间已清理")
        return True
    
    def fix_dashboard(self) -> bool:
        """修复 Dashboard"""
        self.log("🔧 修复 Dashboard...")
        
        # 停止所有 Dashboard 进程
        subprocess.run("pkill -f 'dashboard_v4'", shell=True)
        
        import time
        time.sleep(2)
        
        # 释放端口
        subprocess.run("fuser -k 8081/tcp 2>/dev/null", shell=True)
        
        time.sleep(2)
        
        # 启动 Dashboard
        subprocess.Popen(
            "cd /home/admin/Ziwei/projects && "
            "nohup python3 dashboard_v4_0_1.py > "
            "/home/admin/Ziwei/data/logs/dashboard.log 2>&1 &",
            shell=True
        )
        
        self.log("✅ Dashboard 已修复")
        return True
    
    def fix_supervisor(self) -> bool:
        """修复 Supervisor 服务"""
        self.log("🔧 修复 Supervisor 服务...")
        
        # 重启所有 Supervisor 服务
        subprocess.run("supervisorctl restart all", shell=True)
        
        self.log("✅ Supervisor 服务已重启")
        return True
    
    def run(self):
        """执行分配给该 agent 的所有任务"""
        self.log("\n" + "=" * 80)
        self.log(f"🤖 {self.agent_name} - Agent 任务执行器")
        self.log("=" * 80)
        
        # 加载任务
        task_data = self.load_tasks()
        tasks = task_data.get('tasks', {}).get(self.agent_name, [])
        
        if not tasks:
            self.log("✅ 没有待执行的任务")
            return
        
        self.log(f"📋 待执行任务：{len(tasks)} 个")
        
        # 执行任务
        for task in tasks:
            priority = task.get('priority', 'normal')
            self.log(f"\n🎯 任务优先级：{priority}")
            
            success = self.execute_task(task)
            
            if success:
                self.tasks_completed += 1
                self.log("✅ 任务完成")
                
                # 🧠 学习解决方法
                if LEARNER:
                    LEARNER.learn_problem_solving(
                        problem=task.get('issue', '未知问题'),
                        solution=task.get('suggestion', '无建议'),
                        method=f"Agent {self.agent_name} 执行成功"
                    )
            else:
                self.log("❌ 任务失败")
        
        self.log("\n" + "=" * 80)
        self.log(f"📊 执行完成：{self.tasks_completed}/{len(tasks)} 个任务")
        self.log("=" * 80)
        
        # 🧠 生成学习报告
        if LEARNER and self.tasks_completed > 0:
            self.log("\n" + LEARNER.generate_report())


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python3 agent_executor.py <agent_name>")
        print("agent_name: 爱人 | 信念 | 如意")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    if agent_name not in ['爱人', '信念', '如意']:
        print(f"❌ 未知的 agent: {agent_name}")
        print("有效的 agent: 爱人 | 信念 | 如意")
        sys.exit(1)
    
    executor = AgentExecutor(agent_name)
    executor.run()


if __name__ == "__main__":
    main()
