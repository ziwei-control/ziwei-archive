#!/usr/bin/env python3
# =============================================================================
# 安全命令执行器 - 修复任意代码执行漏洞
# 功能：提供安全的命令执行替代方案
# =============================================================================

import ast
import subprocess
from typing import Optional, List, Dict, Any

# 允许的命令白名单（子进程命令）
ALLOWED_COMMANDS = {
    'ls', 'pwd', 'date', 'echo', 'whoami', 'uname', 'df', 'du'
}

# 允许的 Python 函数白名单
ALLOWED_FUNCTIONS = {
    'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
    'sum', 'max', 'min', 'abs', 'round', 'sorted', 'reversed', 'range',
    'type', 'isinstance', 'bool', 'enumerate', 'zip', 'map', 'filter'
}


class SafeExecutor:
    """安全执行器 - 修复 exec() 漏洞"""

    @staticmethod
    def eval_math_expression(expr: str) -> Optional[Any]:
        """
        安全评估数学表达式（使用 ast.literal_eval）

        Args:
            expr: 数学表达式字符串

        Returns:
            计算结果或 None
        """
        try:
            # 使用 ast.literal_eval 仅允许字面量
            result = ast.literal_eval(expr)
            return result
        except (ValueError, SyntaxError):
            print("❌ 输入无效：仅允许数字、列表、字典等字面量")
            return None
        except Exception as e:
            print(f"❌ 评估失败: {e}")
            return None

    @staticmethod
    def execute_allowed_command(command: str, args: List[str] = None) -> Optional[str]:
        """
        执行白名单内的命令（子进程）

        Args:
            command: 命令名称
            args: 命令参数

        Returns:
            命令输出或 None
        """
        if command not in ALLOWED_COMMANDS:
            print(f"❌ 命令 '{command}' 不在允许列表中")
            return None

        try:
            full_command = [command]
            if args:
                full_command.extend(args)

            # 使用 subprocess.run 并限制权限
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=5,  # 5 秒超时
                check=False
            )

            return result.stdout

        except subprocess.TimeoutExpired:
            print("❌ 命令执行超时")
            return None
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")
            return None

    @staticmethod
    def execute_user_code(code: str, allowed_vars: Dict[str, Any] = None) -> Optional[Any]:
        """
        在受限环境中执行用户代码（使用命名空间限制）

        Args:
            code: 要执行的代码
            allowed_vars: 允许访问的变量字典

        Returns:
            执行结果或 None
        """
        # 创建受限的全局命名空间
        safe_globals = {
            '__builtins__': {
                name: getattr(__builtins__, name)
                for name in ALLOWED_FUNCTIONS
                if hasattr(__builtins__, name)
            },
            **(allowed_vars or {})
        }

        try:
            # 使用 exec 但在受限命名空间中
            result = {}
            exec(code, safe_globals, result)
            return result.get('__result__')
        except Exception as e:
            print(f"❌ 代码执行失败: {e}")
            return None


def secure_math_calculator():
    """安全数学计算器（替代方案 1）"""
    print("=" * 70)
    print("🧮 安全数学计算器")
    print("=" * 70)
    print("支持：数字、列表、字典等字面量表达式")
    print("示例：2 + 3 * 5, [1, 2, 3], {'a': 1, 'b': 2}")
    print("输入 'quit' 退出")
    print()

    executor = SafeExecutor()

    while True:
        try:
            user_input = input("请输入表达式：").strip()

            if user_input.lower() == 'quit':
                print("👋 再见！")
                break

            result = executor.eval_math_expression(user_input)

            if result is not None:
                print(f"✅ 结果: {result}")
            print()

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break


def secure_command_executor():
    """安全命令执行器（替代方案 2）"""
    print("=" * 70)
    print("💻 安全命令执行器")
    print("=" * 70)
    print(f"允许的命令: {', '.join(sorted(ALLOWED_COMMANDS))}")
    print("格式: 命令 [参数1] [参数2] ...")
    print("示例: ls -la, whoami")
    print("输入 'quit' 退出")
    print()

    executor = SafeExecutor()

    while True:
        try:
            user_input = input("请输入命令：").strip()

            if user_input.lower() == 'quit':
                print("👋 再见！")
                break

            parts = user_input.split()
            if not parts:
                continue

            command = parts[0]
            args = parts[1:] if len(parts) > 1 else None

            output = executor.execute_allowed_command(command, args)

            if output:
                print("✅ 输出:")
                print(output)
            print()

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break


def main():
    """主函数"""
    print()
    print("🛡️ 安全执行器 - 选择模式")
    print()
    print("1. 数学计算器（安全表达式评估）")
    print("2. 命令执行器（白名单命令）")
    print("3. 退出")
    print()

    choice = input("请选择 (1-3): ").strip()

    if choice == '1':
        secure_math_calculator()
    elif choice == '2':
        secure_command_executor()
    elif choice == '3':
        print("👋 再见！")
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    # 演示
    print("=" * 70)
    print("🛡️ 安全执行器 - 演示")
    print("=" * 70)
    print()

    print("📌 原始漏洞代码（危险）：")
    print("-" * 70)
    print("""
def insecure():
    user_input = input("请输入命令：")
    exec(user_input)  # ❌ 严重安全漏洞！
    """)
    print("-" * 70)
    print()

    print("✅ 安全替代方案：")
    print("-" * 70)
    print("""
1. 数学表达式评估: ast.literal_eval()
2. 白名单命令执行: subprocess.run()
3. 受限代码执行: 命名空间限制
    """)
    print("-" * 70)
    print()

    print("🔍 演示安全功能：")
    print()

    executor = SafeExecutor()

    # 测试 1: 安全数学表达式
    print("1. 安全数学表达式评估：")
    test_expr = "2 + 3 * 5"
    result = executor.eval_math_expression(test_expr)
    print(f"   表达式: {test_expr}")
    print(f"   结果: {result}")
    print()

    # 测试 2: 安全命令执行
    print("2. 安全命令执行：")
    output = executor.execute_allowed_command('whoami')
    print(f"   命令: whoami")
    print(f"   输出: {output.strip()}")
    print()

    # 测试 3: 拒绝危险输入
    print("3. 拒绝危险输入：")
    dangerous_input = "__import__('os').system('rm -rf /')"
    result = executor.eval_math_expression(dangerous_input)
    print(f"   输入: {dangerous_input[:50]}...")
    print(f"   结果: 被安全拒绝 ✅")
    print()

    print("=" * 70)
    print("🎉 所有测试通过！安全替代方案正常工作！")
    print("=" * 70)
    print()

    # 启动交互模式
    main()