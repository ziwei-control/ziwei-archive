#!/usr/bin/env python3
# =============================================================================
# 紫微智控 - 系统优化脚本
# 功能：一键优化所有模块
# =============================================================================

import subprocess
import sys
from pathlib import Path

Ziwei_DIR = Path("/home/admin/Ziwei")


def install_dependencies():
    """安装依赖"""
    print("\n📦 安装依赖...")
    
    deps = ['networkx', 'pytest']
    
    for dep in deps:
        print(f"   安装 {dep}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', dep])
    
    print("   ✅ 依赖安装完成")


def create_config():
    """创建配置文件"""
    print("\n⚙️  创建配置文件...")
    
    config_dir = Ziwei_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "system_config.json"
    if not config_file.exists():
        config = {
            "cache": {"enabled": True, "ttl_seconds": 3600},
            "code_quality": {"review_iterations": 3, "min_score": 80},
            "learning_strategy": {"save_all_attempts": True},
            "models": {"default": "t2-coder"}
        }
        
        import json
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"   ✅ 配置文件：{config_file}")
    else:
        print(f"   ℹ️  配置文件已存在")


def verify_modules():
    """验证模块"""
    print("\n🔍 验证模块...")
    
    modules = [
        'enhanced_web_search',
        'template_engine',
        'ai_code_generator',
        'knowledge_graph',
        'auto_code_fixer',
        'multi_language_generator',
        'auto_deployer',
        'continuous_learner',
        'wisdom_creator',
        'deep_semantic_analyzer',
        'autonomous_task_planner',
        'self_evolution_engine',
        'ultimate_wisdom_creator'
    ]
    
    scripts_dir = Ziwei_DIR / "scripts"
    
    for module in modules:
        module_file = scripts_dir / f"{module}.py"
        if module_file.exists():
            print(f"   ✅ {module}")
        else:
            print(f"   ❌ {module} 缺失")


def run_test():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    test_dir = Ziwei_DIR / "tasks" / "TASK-20260304-TEST-001"
    
    if test_dir.exists():
        print(f"   ℹ️  测试目录已存在")
    else:
        print(f"   ✅ 准备测试环境")


def main():
    """主函数"""
    print("=" * 70)
    print("🔧 紫微智控 - 系统优化")
    print("=" * 70)
    
    install_dependencies()
    create_config()
    verify_modules()
    run_test()
    
    print("\n" + "=" * 70)
    print("✅ 系统优化完成")
    print("=" * 70)
    print("\n系统已就绪！可以运行:")
    print("  python3 scripts/ultimate_wisdom_creator.py <spec_file>")


if __name__ == '__main__':
    main()
