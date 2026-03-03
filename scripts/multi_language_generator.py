#!/usr/bin/env python3
# =============================================================================
# 多语言代码生成引擎
# 功能：支持 Python/JavaScript/Go 等多语言
# =============================================================================

from pathlib import Path
from datetime import datetime
from typing import Dict, List


class MultiLanguageGenerator:
    """多语言代码生成"""
    
    def __init__(self):
        self.supported_languages = {
            'python': self.generate_python,
            'javascript': self.generate_javascript,
            'typescript': self.generate_typescript,
            'go': self.generate_go,
            'rust': self.generate_rust
        }
        self.language_extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'go': '.go',
            'rust': '.rs'
        }
    
    def select_language(self, spec_text: str) -> str:
        """根据说明书选择语言"""
        # 默认 Python
        language = 'python'
        
        # 检测语言关键词
        if any(kw in spec_text.lower() for kw in ['javascript', 'js', 'node', 'react', 'vue']):
            language = 'javascript'
        elif any(kw in spec_text.lower() for kw in ['typescript', 'ts', 'angular']):
            language = 'typescript'
        elif any(kw in spec_text.lower() for kw in ['go', 'golang']):
            language = 'go'
        elif any(kw in spec_text.lower() for kw in ['rust', 'cargo']):
            language = 'rust'
        
        print(f"\n🌐 选择语言：{language}")
        return language
    
    def generate_python(self, spec: Dict) -> str:
        """生成 Python 代码"""
        return f'''#!/usr/bin/env python3
"""
{spec.get('name', 'Project')} - v1.0.0
{spec.get('description', '')}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
语言：Python
"""

import argparse
import sys
from pathlib import Path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="{spec.get('description', 'Project')}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("input", help="输入文件/目录")
    parser.add_argument("-o", "--output", help="输出文件/目录")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细模式")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    # 主逻辑
    print(f"处理：{{args.input}}")
    if args.output:
        print(f"输出：{{args.output}}")
    if args.verbose:
        print("模式：详细")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def generate_javascript(self, spec: Dict) -> str:
        """生成 JavaScript 代码"""
        return f'''/**
 * {spec.get('name', 'Project')} - v1.0.0
 * {spec.get('description', '')}
 * 
 * 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 语言：JavaScript
 */

const fs = require('fs');
const path = require('path');

/**
 * 主函数
 * @param {string} input - 输入文件/目录
 * @param {string} output - 输出文件/目录
 * @param {boolean} verbose - 详细模式
 */
function main(input, output, verbose = false) {{
    console.log(`处理：${{input}}`);
    
    if (output) {{
        console.log(`输出：${{output}}`);
    }}
    
    if (verbose) {{
        console.log('模式：详细');
    }}
    
    // 主逻辑
    // TODO: 实现具体功能
}}

// CLI 入口
if (require.main === module) {{
    const args = process.argv.slice(2);
    const input = args[0];
    
    if (!input) {{
        console.error('错误：请提供输入文件/目录');
        process.exit(1);
    }}
    
    main(input);
}}

module.exports = {{ main }};
'''
    
    def generate_typescript(self, spec: Dict) -> str:
        """生成 TypeScript 代码"""
        return f'''/**
 * {spec.get('name', 'Project')} - v1.0.0
 * {spec.get('description', '')}
 * 
 * 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 语言：TypeScript
 */

interface Config {{
    input: string;
    output?: string;
    verbose?: boolean;
}}

/**
 * 主函数
 * @param config - 配置对象
 */
export function main(config: Config): number {{
    console.log(`处理：${{config.input}}`);
    
    if (config.output) {{
        console.log(`输出：${{config.output}}`);
    }}
    
    if (config.verbose) {{
        console.log('模式：详细');
    }}
    
    // 主逻辑
    // TODO: 实现具体功能
    
    return 0;
}}

// CLI 入口
if (require.main === module) {{
    const args = process.argv.slice(2);
    const input = args[0];
    
    if (!input) {{
        console.error('错误：请提供输入文件/目录');
        process.exit(1);
    }}
    
    main({{ input }});
}}
'''
    
    def generate_go(self, spec: Dict) -> str:
        """生成 Go 代码"""
        return f'''// {spec.get('name', 'Project')} - v1.0.0
// {spec.get('description', '')}
//
// 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 语言：Go

package main

import (
    "flag"
    "fmt"
    "os"
)

var (
    input   string
    output  string
    verbose bool
    version bool
)

func init() {{
    flag.StringVar(&input, "input", "", "输入文件/目录")
    flag.StringVar(&output, "o", "", "输出文件/目录")
    flag.BoolVar(&verbose, "v", false, "详细模式")
    flag.BoolVar(&version, "version", false, "显示版本")
}}

func main() {{
    flag.Parse()
    
    if version {{
        fmt.Println("{spec.get('name', 'Project')} v1.0.0")
        return
    }}
    
    if input == "" {{
        fmt.Fprintln(os.Stderr, "错误：请提供输入文件/目录")
        os.Exit(1)
    }}
    
    fmt.Printf("处理：%s\\n", input)
    
    if output != "" {{
        fmt.Printf("输出：%s\\n", output)
    }}
    
    if verbose {{
        fmt.Println("模式：详细")
    }}
    
    // 主逻辑
    // TODO: 实现具体功能
}}
'''
    
    def generate_rust(self, spec: Dict) -> str:
        """生成 Rust 代码"""
        return f'''// {spec.get('name', 'Project')} - v1.0.0
// {spec.get('description', '')}
//
// 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 语言：Rust

use std::env;
use std::process;

fn main() {{
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {{
        eprintln!("错误：请提供输入文件/目录");
        process::exit(1);
    }}
    
    let input = &args[1];
    let mut output = String::new();
    let mut verbose = false;
    
    // 解析参数
    for i in 2..args.len() {{
        match args[i].as_str() {{
            "-o" | "--output" => {{
                if i + 1 < args.len() {{
                    output = args[i + 1].clone();
                }}
            }}
            "-v" | "--verbose" => verbose = true,
            _ => {{}}
        }}
    }}
    
    println!("处理：{{}}", input);
    
    if !output.is_empty() {{
        println!("输出：{{}}", output);
    }}
    
    if verbose {{
        println!("模式：详细");
    }}
    
    // 主逻辑
    // TODO: 实现具体功能
}}
'''
    
    def generate(self, spec: Dict, language: str = None) -> Dict:
        """生成多语言代码"""
        if not language:
            language = self.select_language(spec.get('spec_text', ''))
        
        generator = self.supported_languages.get(language)
        
        if not generator:
            print(f"⚠️ 不支持的语言：{language}，使用 Python")
            generator = self.generate_python
        
        code = generator(spec)
        extension = self.language_extensions.get(language, '.txt')
        
        return {
            'code': code,
            'language': language,
            'extension': extension,
            'size': len(code)
        }


def main():
    """主函数"""
    generator = MultiLanguageGenerator()
    
    spec = {
        'name': 'Test Project',
        'description': '这是一个测试项目',
        'spec_text': '创建一个 JavaScript 工具'
    }
    
    result = generator.generate(spec)
    
    print(f"\n生成结果:")
    print(f"  语言：{result['language']}")
    print(f"  扩展名：{result['extension']}")
    print(f"  大小：{result['size']} 字节")
    print(f"\n代码预览:")
    print(result['code'][:500])


if __name__ == '__main__':
    main()
