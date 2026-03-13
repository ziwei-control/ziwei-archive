#!/usr/bin/env python3
# =============================================================================
# 紫微制造 - 系统观察者 v1.0
# 功能：每 8 分钟观察系统一次，发现问题并提出问题给三个 agent
# 任务：分配给 爱人、信念、如意 三个 agent 解决
# =============================================================================

import json
import hashlib
import os
import sys
import time
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
Ziwei_DIR = Path("/home/admin/Ziwei")
OBSERVER_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "observer.log"
OBSERVER_REPORT = Ziwei_DIR / "data" / "logs" / "observer" / "observer_report.json"
TASK_QUEUE = Ziwei_DIR / "data" / "strategy" / "observer_tasks.json"
DASHBOARD_URL = "http://localhost:8081"
LEARNING_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "learning.log"
DECISION_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "decisions.log"
KNOWLEDGE_BASE = Ziwei_DIR / "data" / "knowledge" / "work_methodology.json"

# 日志配置 - 每个日志文件最大 10MB，保留 3 个备份
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_BACKUP_COUNT = 3

# 确保目录存在
OBSERVER_LOG.parent.mkdir(parents=True, exist_ok=True)
LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE.parent.mkdir(parents=True, exist_ok=True)

# 导入学习和决策模块
sys.path.insert(0, str(Ziwei_DIR / "scripts"))
try:
    from observer_learning import ObserverLearner
    LEARNER = ObserverLearner()
except Exception as e:
    print(f"⚠️  学习模块加载失败：{e}")
    LEARNER = None

try:
    from auto_decision import AutoDecision
    DECISION_ENGINE = AutoDecision()
except Exception as e:
    print(f"⚠️  决策引擎加载失败：{e}")
    DECISION_ENGINE = None

class SystemObserver:
    """系统观察者 - 时刻观察系统运行状态"""
    
    def __init__(self):
        self.observation_count = 0
        self.last_observation = None
        self.issues_found = []
        # 🧠 问题去重缓存 - 记录已报告的问题，避免重复
        self.issue_cache = {}  # {issue_key: last_reported_time}
        self.CACHE_EXPIRE_SECONDS = 600  # 10 分钟过期
        
    def log(self, message: str):
        """记录日志（带自动轮转）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}\n"
        
        # 检查是否需要轮转
        self._rotate_log_if_needed(OBSERVER_LOG)
        
        # 写入日志文件
        with open(OBSERVER_LOG, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        # 同时输出到 stdout（减少输出）
        if '检查' in message or '完成' in message or '❌' in message or '⚠️' in message or '✅' in message:
            print(log_line, end='')
    
    def _rotate_log_if_needed(self, log_file: Path):
        """检查并轮转日志文件"""
        if not log_file.exists():
            return
        
        current_size = log_file.stat().st_size
        if current_size < MAX_LOG_SIZE:
            return
        
        # 轮转日志
        self.log(f"🔄 日志文件超过 {MAX_LOG_SIZE // (1024*1024)}MB，开始轮转...")
        
        # 删除最旧的备份
        oldest_backup = Path(f"{log_file}.{MAX_BACKUP_COUNT}")
        if oldest_backup.exists():
            oldest_backup.unlink()
        
        # 重命名现有备份
        for i in range(MAX_BACKUP_COUNT - 1, 0, -1):
            old_file = Path(f"{log_file}.{i}")
            new_file = Path(f"{log_file}.{i + 1}")
            if old_file.exists():
                old_file.rename(new_file)
        
        # 当前日志重命名为 .1
        backup_file = Path(f"{log_file}.1")
        log_file.rename(backup_file)
        
        self.log(f"✅ 日志轮转完成：{log_file.name} → {backup_file.name}")
    

    def deduplicate_issues(self, issues: list) -> list:
        """问题去重 - 过滤掉重复的问题"""
        unique_issues = []
        current_time = datetime.now().timestamp()
        
        for issue in issues:
            # 生成问题的唯一标识符
            issue_key = self._generate_issue_key(issue)
            
            # 检查缓存
            if issue_key in self.issue_cache:
                last_reported = self.issue_cache[issue_key]
                time_diff = current_time - last_reported
                
                # 如果在缓存期内（10分钟），跳过
                if time_diff < self.CACHE_EXPIRE_SECONDS:
                    self.log(f"🔄 跳过重复问题：{issue.get('issue', '')}（{int(time_diff)}秒前已报告）")
                    continue
                else:
                    self.log(f"⏰ 问题缓存已过期，重新报告：{issue.get('issue', '')}")
            
            # 检查修复历史（避免重复修复）
            if self._is_recently_fixed(issue):
                self.log(f"🔧 问题已在最近修复过，跳过：{issue.get('issue', '')}")
                continue
            
            # 添加到缓存和结果列表
            self.issue_cache[issue_key] = current_time
            unique_issues.append(issue)
        
        # 清理过期的缓存项
        self._cleanup_cache(current_time)
        
        return unique_issues
    
    def _generate_issue_key(self, issue: dict) -> str:
        """生成问题的唯一标识符（不使用hashlib）"""
        # 使用问题类型、组件和问题描述生成唯一key
        key_parts = [
            issue.get('type', ''),
            issue.get('component', ''),
            issue.get('issue', '')
        ]
        key_string = '|'.join(key_parts)
        # 使用字符串的hash函数替代hashlib
        return str(hash(key_string))
    
    def _is_recently_fixed(self, issue: dict) -> bool:
        """检查问题是否在最近被修复过"""
        FIX_LOG = Ziwei_DIR / "data" / "logs" / "observer" / "fix_log.json"
        
        if not FIX_LOG.exists():
            return False
        
        try:
            with open(FIX_LOG, 'r', encoding='utf-8') as f:
                fix_history = json.load(f)
            
            current_time = datetime.now()
            from datetime import timedelta
            recent_time_threshold = timedelta(minutes=30)  # 30分钟内的修复
            
            issue_text = issue.get('issue', '')
            
            for fix in fix_history[-20:]:  # 检查最近20条修复记录
                fix_time = datetime.fromisoformat(fix.get('timestamp', ''))
                if fix.get('status') == 'success' and (current_time - fix_time) < recent_time_threshold:
                    if issue_text in fix.get('issue', '') or fix.get('issue', '') in issue_text:
                        return True
            
            return False
        except Exception as e:
            self.log(f"⚠️  检查修复历史失败：{e}")
            return False
    
    def _cleanup_cache(self, current_time: float):
        """清理过期的缓存项"""
        expired_keys = []
        for key, timestamp in self.issue_cache.items():
            if current_time - timestamp > self.CACHE_EXPIRE_SECONDS:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.issue_cache[key]
        
        if expired_keys:
            self.log(f"🧹 清理了 {len(expired_keys)} 个过期的问题缓存")

    def observe_system(self) -> Dict:
        """观察系统运行状态"""
        self.log("=" * 80)
        self.log("👁️  开始系统观察...")
        self.log("=" * 80)
        
        observation = {
            'timestamp': datetime.now().isoformat(),
            'observation_id': self.observation_count + 1,
            'issues': [],
            'warnings': [],
            'status': 'normal'
        }
        
        # 1. 观察进程状态
        self.log("\n📊 检查进程状态...")
        process_issues = self.check_processes()
        observation['issues'].extend(process_issues)
        
        # 2. 观察端口状态
        self.log("\n🌐 检查端口状态...")
        port_issues = self.check_ports()
        observation['issues'].extend(port_issues)
        
        # 3. 观察磁盘空间
        self.log("\n💾 检查磁盘空间...")
        disk_issues = self.check_disk_space()
        observation['warnings'].extend(disk_issues)
        
        # 4. 观察交易数据
        self.log("\n📈 检查交易数据...")
        trade_issues = self.check_trade_data()
        observation['issues'].extend(trade_issues)
        
        # 5. 观察 Supervisor 状态
        self.log("\n🔧 检查 Supervisor 状态...")
        supervisor_issues = self.check_supervisor()
        observation['issues'].extend(supervisor_issues)
        
        # 6. 观察日志错误
        self.log("\n📝 检查日志错误...")
        log_issues = self.check_log_errors()
        observation['warnings'].extend(log_issues)
        
        # 7. 观察 Dashboard 页面内容
        self.log("\n🌐 检查 Dashboard 页面内容...")
        dashboard_issues = self.check_dashboard_content()
        observation['issues'].extend(dashboard_issues)
        
        # 统计问题
        total_issues = len(observation['issues'])
        total_warnings = len(observation['warnings'])
        
        if total_issues > 0:
            observation['status'] = 'critical' if total_issues > 3 else 'warning'
        elif total_warnings > 0:
            observation['status'] = 'warning'
        else:
            observation['status'] = 'normal'
        
        self.log("\n" + "=" * 80)
        self.log(f"✅ 观察完成 | 发现 {total_issues} 个问题，{total_warnings} 个警告")
        self.log("=" * 80)
        
        # 🧠 问题去重 - 过滤掉重复的问题
        observation['issues'] = self.deduplicate_issues(observation['issues'])
        observation['warnings'] = self.deduplicate_issues(observation['warnings'])
        
        # 统计去重后的问题
        total_issues = len(observation['issues'])
        total_warnings = len(observation['warnings'])
        
        self.log(f"✅ 观察完成 | 发现 {total_issues} 个问题，{total_warnings} 个警告（已去重）")
        self.log("=" * 80)
        
        self.observation_count += 1
        self.last_observation = observation
        
        return observation
    
    def check_processes(self) -> List[Dict]:
        """检查进程状态"""
        issues = []
        
        # 检查策略引擎进程数量
        result = subprocess.run(
            "ps aux | grep -E 'strategy_engine|soul_trader' | grep -v grep | wc -l",
            shell=True, capture_output=True, text=True
        )
        count = int(result.stdout.strip())
        
        if count == 0:
            issues.append({
                'type': 'critical',
                'component': '策略引擎',
                'issue': '策略引擎未运行',
                'assigned_to': '信念',
                'priority': 'high',
                'suggestion': '立即启动策略引擎'
            })
            self.log("  ❌ 策略引擎未运行")
        elif count > 1:
            issues.append({
                'type': 'warning',
                'component': '策略引擎',
                'issue': f'策略引擎运行 {count} 个进程（正常应为 1 个）',
                'assigned_to': '信念',
                'priority': 'medium',
                'suggestion': '清理重复进程，保留 1 个'
            })
            self.log(f"  ⚠️  策略引擎运行 {count} 个进程（应为 1 个）")
        else:
            self.log("  ✅ 策略引擎运行正常 (1 个进程)")
        
        # 检查 Dashboard 进程（检测所有 Dashboard 相关进程）
        result = subprocess.run(
            "ps aux | grep -E '(dashboard_v4|x402_dashboard)' | grep -v grep | wc -l",
            shell=True, capture_output=True, text=True
        )
        count = int(result.stdout.strip())
        
        if count == 0:
            issues.append({
                'type': 'warning',
                'component': 'Dashboard',
                'issue': 'Dashboard 未运行',
                'assigned_to': '如意',
                'priority': 'low',
                'suggestion': '启动 Dashboard 服务'
            })
            self.log("  ❌ Dashboard 未运行")
        elif count > 1:
            issues.append({
                'type': 'warning',
                'component': 'Dashboard',
                'issue': f'Dashboard 运行 {count} 个进程（正常应为 1 个）',
                'assigned_to': '如意',
                'priority': 'medium',
                'suggestion': '清理重复 Dashboard 进程，保留 1 个'
            })
            self.log(f"  ⚠️  Dashboard 运行 {count} 个进程（应为 1 个）")
        else:
            self.log(f"  ✅ Dashboard 运行正常 (1 个进程)")
        
        return issues
    
    def check_ports(self) -> List[Dict]:
        """检查端口状态"""
        issues = []
        ports = {
            '8081': 'Dashboard',
            '9001': 'Supervisor Web UI',
            '5002': 'x402 API'
        }
        
        for port, service in ports.items():
            result = subprocess.run(
                f"lsof -i :{port} 2>/dev/null | grep LISTEN | wc -l",
                shell=True, capture_output=True, text=True
            )
            count = int(result.stdout.strip())
            
            if count == 0:
                issues.append({
                    'type': 'warning',
                    'component': service,
                    'issue': f'{service} 端口 {port} 未监听',
                    'assigned_to': '如意',
                    'priority': 'low',
                    'suggestion': f'检查 {service} 服务状态'
                })
                self.log(f"  ❌ {service} 端口 {port} 未监听")
            else:
                self.log(f"  ✅ {service} 端口 {port} 正常")
        
        return issues
    
    def check_disk_space(self) -> List[Dict]:
        """检查磁盘空间"""
        issues = []
        
        result = subprocess.run(
            "df -h /home | tail -1 | awk '{print $5}'",
            shell=True, capture_output=True, text=True
        )
        usage = int(result.stdout.strip().replace('%', ''))
        
        if usage > 90:
            issues.append({
                'type': 'critical',
                'component': '磁盘空间',
                'issue': f'磁盘使用率 {usage}%（超过 90%）',
                'assigned_to': '爱人',
                'priority': 'high',
                'suggestion': '清理日志文件或扩展磁盘'
            })
            self.log(f"  ❌ 磁盘使用率 {usage}%（超过 90%）")
        elif usage > 80:
            issues.append({
                'type': 'warning',
                'component': '磁盘空间',
                'issue': f'磁盘使用率 {usage}%（超过 80%）',
                'assigned_to': '爱人',
                'priority': 'medium',
                'suggestion': '准备清理日志文件'
            })
            self.log(f"  ⚠️  磁盘使用率 {usage}%")
        else:
            self.log(f"  ✅ 磁盘使用率 {usage}% 正常")
        
        return issues
    
    def check_trade_data(self) -> List[Dict]:
        """检查交易数据"""
        issues = []
        
        # 检查交易历史文件
        trade_file = Ziwei_DIR / "data" / "strategy" / "trade_history.jsonl"
        if not trade_file.exists():
            issues.append({
                'type': 'critical',
                'component': '交易数据',
                'issue': '交易历史文件不存在',
                'assigned_to': '信念',
                'priority': 'high',
                'suggestion': '检查策略引擎是否正常运行'
            })
            self.log("  ❌ 交易历史文件不存在")
            return issues
        
        # 检查交易数据
        try:
            with open(trade_file, 'r', encoding='utf-8') as f:
                trades = [json.loads(line) for line in f if line.strip()]
            
            # 检查异常交易
            abnormal = [t for t in trades if t.get('value', 0) < 1.0]
            
            if len(abnormal) > 0:
                issues.append({
                    'type': 'warning',
                    'component': '交易数据',
                    'issue': f'发现 {len(abnormal)} 笔异常交易（价值<$1）',
                    'assigned_to': '信念',
                    'priority': 'medium',
                    'suggestion': '清理异常交易数据'
                })
                self.log(f"  ⚠️  发现 {len(abnormal)} 笔异常交易")
            else:
                self.log(f"  ✅ 交易数据正常 ({len(trades)} 笔交易)")
            
            # 检查重复进程
            result = subprocess.run(
                "ps aux | grep 'strategy_engine_v3' | grep -v grep | wc -l",
                shell=True, capture_output=True, text=True
            )
            count = int(result.stdout.strip())
            
            if count > 1:
                issues.append({
                    'type': 'warning',
                    'component': '策略引擎',
                    'issue': f'检测到 {count} 个策略引擎进程',
                    'assigned_to': '信念',
                    'priority': 'medium',
                    'suggestion': '清理重复进程'
                })
                self.log(f"  ⚠️  策略引擎进程数：{count}")
        
        except Exception as e:
            issues.append({
                'type': 'critical',
                'component': '交易数据',
                'issue': f'读取交易数据失败：{e}',
                'assigned_to': '信念',
                'priority': 'high',
                'suggestion': '检查文件权限和格式'
            })
            self.log(f"  ❌ 读取交易数据失败：{e}")
        
        return issues
    
    def check_supervisor(self) -> List[Dict]:
        """检查 Supervisor 状态"""
        issues = []
        
        result = subprocess.run(
            "supervisorctl status 2>/dev/null | grep -c 'FATAL\\|BACKOFF'",
            shell=True, capture_output=True, text=True
        )
        fatal_count = int(result.stdout.strip())
        
        if fatal_count > 0:
            issues.append({
                'type': 'warning',
                'component': 'Supervisor',
                'issue': f'{fatal_count} 个 Supervisor 服务异常',
                'assigned_to': '如意',
                'priority': 'low',
                'suggestion': '检查 Supervisor 服务日志'
            })
            self.log(f"  ⚠️  {fatal_count} 个 Supervisor 服务异常")
        else:
            self.log("  ✅ Supervisor 服务正常")
        
        return issues
    
    def check_log_errors(self) -> List[Dict]:
        """检查日志错误"""
        issues = []
        
        # 检查策略引擎日志
        log_file = Ziwei_DIR / "data" / "logs" / "soul-trader" / "strategy_engine_v3.log"
        if log_file.exists():
            result = subprocess.run(
                f"tail -100 {log_file} 2>/dev/null | grep -c '错误\\|异常\\|Exception'",
                shell=True, capture_output=True, text=True
            )
            error_count = int(result.stdout.strip())
            
            if error_count > 0:
                issues.append({
                    'type': 'warning',
                    'component': '策略引擎日志',
                    'issue': f'最近日志中有 {error_count} 条错误',
                    'assigned_to': '信念',
                    'priority': 'low',
                    'suggestion': '查看日志详情'
                })
                self.log(f"  ⚠️  策略引擎日志中有 {error_count} 条错误")
        
        return issues
    
    def check_dashboard_content(self) -> List[Dict]:
        """检查 Dashboard 页面内容"""
        issues = []
        
        try:
            # 访问 Dashboard 页面
            self.log("  正在访问 Dashboard 页面...")
            req = urllib.request.Request(DASHBOARD_URL, headers={'User-Agent': 'Ziwei-Observer/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')
            
            self.log("  ✅ Dashboard 页面访问成功")
            
            # 检查关键内容
            checks = {
                '我的持仓': '我的持仓' in content,
                '持仓详情': '持仓详情' in content,
                '交易时间线': '交易时间线' in content,
                '建仓': '建仓' in content,
                '清仓': '清仓' in content,
                '加密货币价格': '加密货币价格' in content or 'BTC' in content,
                '加载失败': '加载失败' in content,
                'tuple indices': 'tuple indices' in content,
            }
            
            # 报告问题
            if not checks['我的持仓']:
                issues.append({
                    'type': 'critical',
                    'component': 'Dashboard',
                    'issue': 'Dashboard 未显示我的持仓卡片',
                    'assigned_to': '如意',
                    'priority': 'high',
                    'suggestion': '检查 dashboard_trading_card.py 和数据文件'
                })
                self.log("  ❌ 未显示我的持仓卡片")
            else:
                self.log("  ✅ 我的持仓卡片显示正常")
            
            if not checks['交易时间线']:
                issues.append({
                    'type': 'warning',
                    'component': 'Dashboard',
                    'issue': 'Dashboard 未显示交易时间线',
                    'assigned_to': '如意',
                    'priority': 'medium',
                    'suggestion': '检查交易历史数据'
                })
                self.log("  ❌ 未显示交易时间线")
            else:
                self.log("  ✅ 交易时间线显示正常")
            
            if checks['加载失败']:
                issues.append({
                    'type': 'critical',
                    'component': 'Dashboard',
                    'issue': 'Dashboard 显示加载失败错误',
                    'assigned_to': '信念',
                    'priority': 'high',
                    'suggestion': '检查错误日志和代码'
                })
                self.log("  ❌ 显示加载失败错误")
            
            if checks['tuple indices']:
                issues.append({
                    'type': 'critical',
                    'component': 'Dashboard',
                    'issue': 'Dashboard 显示 Python 代码错误（tuple indices）',
                    'assigned_to': '信念',
                    'priority': 'high',
                    'suggestion': '修复 dashboard_trading_card.py 中的 portfolio.items() 调用'
                })
                self.log("  ❌ 显示 Python 代码错误")
            
            # 检查是否有真实交易记录
            if '暂无真实交易记录' in content:
                self.log("  ℹ️  无真实交易记录（正常）")
            
            # 统计检查结果
            passed = sum(1 for k, v in checks.items() if v and k not in ['加载失败', 'tuple indices'])
            total = len(checks) - 2  # 排除错误检查
            self.log(f"  📊 Dashboard 内容检查：{passed}/{total} 通过")
            
        except urllib.error.URLError as e:
            issues.append({
                'type': 'critical',
                'component': 'Dashboard',
                'issue': f'无法访问 Dashboard 页面：{e}',
                'assigned_to': '如意',
                'priority': 'high',
                'suggestion': '检查 Dashboard 进程和端口'
            })
            self.log(f"  ❌ 无法访问 Dashboard 页面：{e}")
        except Exception as e:
            issues.append({
                'type': 'warning',
                'component': 'Dashboard',
                'issue': f'检查 Dashboard 页面失败：{e}',
                'assigned_to': '如意',
                'priority': 'medium',
                'suggestion': '检查网络连接和代码'
            })
            self.log(f"  ❌ 检查 Dashboard 页面失败：{e}")
        
        return issues
    
    def assign_tasks(self, observation: Dict):
        """分配任务给三个 agent"""
        issues = observation.get('issues', [])
        warnings = observation.get('warnings', [])
        
        # 按 agent 分组任务
        tasks = {
            '爱人': [],
            '信念': [],
            '如意': []
        }
        
        for issue in issues + warnings:
            assigned_to = issue.get('assigned_to', '信念')
            if assigned_to in tasks:
                tasks[assigned_to].append(issue)
        
        # 保存任务队列
        task_queue = {
            'timestamp': datetime.now().isoformat(),
            'observation_id': observation['observation_id'],
            'tasks': tasks,
            'total_issues': len(issues),
            'total_warnings': len(warnings)
        }
        
        with open(TASK_QUEUE, 'w', encoding='utf-8') as f:
            json.dump(task_queue, f, indent=2, ensure_ascii=False)
        
        self.log("\n📋 任务分配:")
        for agent, agent_tasks in tasks.items():
            if agent_tasks:
                self.log(f"  → {agent}: {len(agent_tasks)} 个任务")
                for task in agent_tasks:
                    self.log(f"    - [{task['priority']}] {task['issue']}")
            else:
                self.log(f"  → {agent}: 无任务")
        
        # 保存观察报告
        observation['tasks_assigned'] = tasks
        with open(OBSERVER_REPORT, 'w', encoding='utf-8') as f:
            json.dump(observation, f, indent=2, ensure_ascii=False)
        
        self.log(f"\n💾 观察报告已保存：{OBSERVER_REPORT}")
        self.log(f"💾 任务队列已保存：{TASK_QUEUE}")
        
        # 🧠 学习和总结
        if LEARNER:
            self.learn_from_observation(observation)
    
    def learn_from_observation(self, observation: Dict):
        """从观察中学习"""
        issues = observation.get('issues', [])
        
        # 学习重复进程问题
        for issue in issues:
            if '进程' in issue.get('issue', '') and '重复' in issue.get('issue', ''):
                LEARNER.learn_problem_solving(
                    problem=issue.get('issue'),
                    solution="清理旧进程 + Supervisor 统一管理",
                    method="1. pkill 清理旧进程 2. supervisorctl restart 重启服务 3. 验证进程数量"
                )
            
            if '加仓' in issue.get('issue', '') or '仓位' in issue.get('issue', ''):
                LEARNER.learn_principle(
                    principle="综合保护策略",
                    explanation="防止无限加仓，控制风险",
                    examples=[
                        "限制加仓次数（最多 3 次）",
                        "禁止亏损加仓",
                        "单币种仓位上限（20%）"
                    ]
                )
        
        # 记录观察统计
        total_issues = len(issues)
        if total_issues == 0:
            LEARNER.log("✅ 系统运行正常，无问题发现")
        else:
            LEARNER.log(f"📊 本次观察发现 {total_issues} 个问题，已分配任务")
    
    def auto_fix_issues(self, issues: list):
        """自动修复问题"""
        if not DECISION_ENGINE:
            return
        
        for issue in issues:
            context = {
                'type': 'process_management' if '进程' in issue.get('issue', '') else 'other',
                'problem': issue.get('issue', ''),
                'risk': 'low' if '重复' in issue.get('issue', '') else 'medium',
                'default_method': issue.get('suggestion', '')
            }
            
            decision = DECISION_ENGINE.make_decision(context)
            
            if decision.get('action') == 'execute':
                self.log(f"🤖 自动执行：{issue.get('issue', '')}")
                self.log(f"   方法：{decision.get('method', '')}")
                self.log(f"   原因：{decision.get('reason', '')}")
                
                # 执行修复
                if '进程' in issue.get('issue', '') and '重复' in issue.get('issue', ''):
                    import subprocess
                    subprocess.run("pkill -f strategy_engine_v3.py 2>/dev/null || true", shell=True)
                    subprocess.run("sleep 2 && supervisorctl restart ziwei-strategy-engine", shell=True)
                    self.log("✅ 已自动清理重复进程")
        """运行观察者"""
        self.log("\n" + "=" * 80)
        self.log("👁️  紫微制造 - 系统观察者 v1.0")
        self.log("=" * 80)
        self.log(f"🕐 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("🔄 观察间隔：60 分钟（优化后）")
        self.log("=" * 80)
        
        # 执行观察
        observation = self.observe_system()
        
        # 🧠 去重后统计
        unique_issues = len(observation['issues'])
        unique_warnings = len(observation['warnings'])
        
        # 分配任务（只分配去重后的问题）
        if unique_issues > 0 or unique_warnings > 0:
            self.log(f"\n📋 发现 {unique_issues} 个新问题，{unique_warnings} 个新警告（已去重）")
            self.assign_tasks(observation)
        else:
            self.log("\n✅ 系统运行正常，无新问题")
        
        self.log("\n" + "=" * 80)
        self.log("✅ 观察完成")
        self.log("=" * 80)
    
    def run(self):
        """运行观察者"""
        self.log("\n" + "=" * 80)
        self.log("👁️  紫微制造 - 系统观察者 v1.0")
        self.log("=" * 80)
        self.log(f"🕐 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"🔄 观察间隔：8 分钟")
        self.log("=" * 80)
        
        # 执行观察
        observation = self.observe_system()
        
        # 🧠 学习
        if LEARNER:
            self.learn_from_observation(observation)
        
        # 🤖 自动决策并执行
        if DECISION_ENGINE and observation['issues']:
            self.auto_fix_issues(observation['issues'])
        
        # 分配任务（如果还有未自动修复的）
        if observation['issues'] or observation['warnings']:
            self.assign_tasks(observation)
        else:
            self.log("\n✅ 系统运行正常，无需分配任务")
        
        self.log("\n" + "=" * 80)
        self.log("✅ 观察完成")
        self.log("=" * 80)


def main():
    """主函数"""
    observer = SystemObserver()
    observer.run()


if __name__ == "__main__":
    main()
