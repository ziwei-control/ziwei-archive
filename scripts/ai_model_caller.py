#!/usr/bin/env python3
# =============================================================================
# AI 模型调用引擎 v2.0
# 功能：多方式调用 AI 模型，确保成功率
# =============================================================================

import subprocess
import os
import json
from pathlib import Path
from typing import Optional, Dict


class AIModelCaller:
    """AI 模型调用引擎"""
    
    def __init__(self):
        self.models = {
            't1-architect': '首席架构师',
            't2-coder': '代码特种兵',
            't3-auditor': '代码审计员',
            't4-logic': '逻辑推理机',
            't5-translator': '跨域翻译家',
            't6-reader': '长文解析器'
        }
        self.config_file = Path('/home/admin/Ziwei/config/ai_models.json')
        self.cache_dir = Path('/home/admin/Ziwei/data/ai_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def call_openclaw_cli(self, model: str, prompt: str, timeout: int = 120) -> Optional[str]:
        """通过 openclaw CLI 调用"""
        try:
            print(f"   🤖 调用 openclaw CLI ({model})...")
            
            result = subprocess.run(
                ['openclaw', 'ask', '--model', model, prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd='/home/admin/Ziwei',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            if result.returncode == 0 and result.stdout.strip():
                code = result.stdout.strip()
                # 清理代码块标记
                if '```python' in code:
                    code = code.split('```python')[1].split('```')[0]
                elif '```' in code:
                    code = code.split('```')[1].split('```')[0]
                
                print(f"   ✅ openclaw CLI 成功：{len(code)} 字节")
                return code
            else:
                print(f"   ⚠️ openclaw CLI 失败 (returncode={result.returncode})")
                if result.stderr:
                    print(f"   错误：{result.stderr[:200]}")
                return None
                
        except FileNotFoundError:
            print(f"   ⚠️ openclaw CLI 未找到")
            return None
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ openclaw CLI 超时 ({timeout}秒)")
            return None
        except Exception as e:
            print(f"   ⚠️ openclaw CLI 错误：{e}")
            return None
    
    def call_sessions_spawn(self, model: str, prompt: str, timeout: int = 120) -> Optional[str]:
        """通过 sessions_spawn 调用"""
        try:
            print(f"   🤖 调用 sessions_spawn ({model})...")
            
            # 尝试导入
            try:
                from tools import sessions_spawn
                
                result = sessions_spawn(
                    task=prompt,
                    agentId=model,
                    timeoutSeconds=timeout
                )
                
                if result and 'code' in result:
                    code = result['code']
                    print(f"   ✅ sessions_spawn 成功：{len(code)} 字节")
                    return code
                else:
                    print(f"   ⚠️ sessions_spawn 无结果")
                    return None
                    
            except ImportError:
                print(f"   ⚠️ sessions_spawn 不可用")
                return None
                
        except Exception as e:
            print(f"   ⚠️ sessions_spawn 错误：{e}")
            return None
    
    def call_with_cache(self, model: str, prompt: str, use_cache: bool = True) -> Optional[str]:
        """带缓存的调用"""
        # 生成缓存 key
        import hashlib
        cache_key = hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.txt"
        
        # 尝试从缓存读取
        if use_cache and cache_file.exists():
            print(f"   💾 从缓存读取...")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # 调用 AI 模型
        code = None
        
        # 方式 1: openclaw CLI
        code = self.call_openclaw_cli(model, prompt)
        if code:
            if use_cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(code)
            return code
        
        # 方式 2: sessions_spawn
        code = self.call_sessions_spawn(model, prompt)
        if code:
            if use_cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(code)
            return code
        
        return None
    
    def generate_code(self, task_type: str, spec: Dict, requirements: list) -> str:
        """生成代码（智能选择模型）"""
        
        # 根据任务类型选择模型
        model_map = {
            'cli_tool': 't2-coder',
            'web_app': 't2-coder',
            'api_service': 't2-coder',
            'bot': 't2-coder',
            'data_processing': 't2-coder'
        }
        
        model = model_map.get(task_type, 't2-coder')
        
        # 构建提示词
        prompt = self._build_prompt(task_type, spec, requirements)
        
        # 调用 AI 模型
        code = self.call_with_cache(model, prompt)
        
        if not code:
            print(f"   ⚠️ AI 模型调用失败，使用模板降级")
            code = self._generate_template_code(task_type, spec)
        
        return code
    
    def _build_prompt(self, task_type: str, spec: Dict, requirements: list) -> str:
        """构建 AI 提示词"""
        return f"""
你是一个专业的 Python 开发工程师。

任务类型：{task_type}
任务名称：{spec.get('name', 'Project')}
任务描述：{spec.get('description', '')}

功能需求:
{chr(10).join(f"- {req}" for req in requirements)}

请生成完整、可运行、符合 PEP8 规范的 Python 代码。

要求:
1. 完整的功能实现
2. 详细的文档字符串
3. 完善的错误处理
4. 符合 Python 最佳实践
5. 代码要有注释
6. 使用 pathlib 处理文件路径
7. 使用 argparse 处理命令行参数

请只返回代码，不要其他说明。
"""
    
    def _generate_template_code(self, task_type: str, spec: Dict) -> str:
        """生成模板代码（降级方案）"""
        return f'''#!/usr/bin/env python3
"""
{spec.get('name', 'Project')} - v1.0.0
{spec.get('description', '')}
"""

import argparse
import sys
from pathlib import Path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="{spec.get('description', 'Project')}"
    )
    parser.add_argument("input", help="输入文件/目录")
    parser.add_argument("-o", "--output", help="输出文件/目录")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细模式")
    
    args = parser.parse_args()
    
    print(f"处理：{{args.input}}")
    if args.output:
        print(f"输出：{{args.output}}")
    if args.verbose:
        print("模式：详细")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def main():
    """测试函数"""
    caller = AIModelCaller()
    
    spec = {
        'name': 'Test Project',
        'description': '这是一个测试项目'
    }
    
    code = caller.generate_code('cli_tool', spec, ['功能 1', '功能 2'])
    
    print(f"\n生成代码长度：{len(code)} 字节")
    print(code[:500])


if __name__ == '__main__':
    main()
