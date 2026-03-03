#!/usr/bin/env python3
# =============================================================================
# 项目模板引擎
# 功能：根据说明书自动选择并应用模板
# =============================================================================

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

Ziwei_DIR = Path("/home/admin/Ziwei")
TEMPLATES_DIR = Ziwei_DIR / "templates"


class ProjectTemplateEngine:
    """项目模板引擎"""
    
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self) -> Dict:
        """加载模板库"""
        templates = {
            'cli_tool': {
                'keywords': ['工具', '命令行', 'batch', 'rename', 'convert', 'query'],
                'structure': {
                    'src': ['main.py'],
                    'tests': ['test_main.py'],
                    'docs': ['README.md'],
                    '': ['requirements.txt']
                },
                'base_score': 70
            },
            'web_app': {
                'keywords': ['网站', 'web', 'Flask', 'FastAPI', '页面', 'HTML'],
                'structure': {
                    'app': ['__init__.py', 'main.py', 'routes.py'],
                    'templates': ['index.html'],
                    'tests': ['test_app.py'],
                    '': ['requirements.txt', 'config.py']
                },
                'base_score': 70
            },
            'api_service': {
                'keywords': ['API', 'REST', '服务', 'endpoint', 'JSON'],
                'structure': {
                    'api': ['__init__.py', 'routes.py', 'schemas.py'],
                    'core': ['config.py', 'security.py'],
                    'tests': ['test_api.py'],
                    '': ['requirements.txt']
                },
                'base_score': 70
            },
            'bot': {
                'keywords': ['机器人', 'bot', 'Telegram', 'Discord', '自动', '通知'],
                'structure': {
                    'bot': ['__init__.py', 'handlers.py', 'services.py'],
                    'config': ['settings.py'],
                    'tests': ['test_bot.py'],
                    '': ['requirements.txt']
                },
                'base_score': 70
            },
            'data_analysis': {
                'keywords': ['分析', 'data', '统计', '可视化', 'chart', '报表'],
                'structure': {
                    'src': ['data_loader.py', 'analyzer.py', 'visualizer.py'],
                    'data': ['raw/.gitkeep', 'processed/.gitkeep'],
                    'notebooks': ['analysis.ipynb'],
                    'tests': ['test_analysis.py'],
                    '': ['requirements.txt']
                },
                'base_score': 70
            }
        }
        
        return templates
    
    def select_template(self, spec_text: str) -> str:
        """根据说明书选择最佳模板"""
        scores = {}
        
        for template_name, template in self.templates.items():
            score = template['base_score']
            
            # 关键词匹配
            for keyword in template['keywords']:
                if keyword.lower() in spec_text.lower():
                    score += 10
            
            # 功能匹配
            if '功能需求' in spec_text:
                func_section = spec_text.split('功能需求')[1].split('技术栈')[0]
                for keyword in template['keywords']:
                    if keyword.lower() in func_section.lower():
                        score += 5
            
            scores[template_name] = score
        
        # 返回得分最高的模板
        best_template = max(scores, key=scores.get)
        print(f"\n📋 模板选择：{best_template} (得分：{scores[best_template]})")
        
        return best_template
    
    def apply_template(self, template_name: str, output_dir: str, spec: Dict) -> List[str]:
        """应用模板到项目"""
        template = self.templates.get(template_name)
        if not template:
            print(f"⚠️ 模板不存在：{template_name}")
            return []
        
        output_path = Path(output_dir)
        created_files = []
        
        print(f"\n🔧 应用模板：{template_name}")
        
        # 创建目录结构
        for dir_name, files in template['structure'].items():
            dir_path = output_path / dir_name if dir_name else output_path
            dir_path.mkdir(parents=True, exist_ok=True)
            
            for file_template in files:
                file_path = dir_path / file_template
                
                # 跳过.gitkeep
                if file_template.endswith('.gitkeep'):
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.touch()
                    created_files.append(str(file_path))
                    continue
                
                # 生成文件内容
                content = self.generate_file_content(file_template, spec)
                
                if content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created_files.append(str(file_path))
                    print(f"   ✅ {file_path}")
        
        return created_files
    
    def generate_file_content(self, filename: str, spec: Dict) -> str:
        """生成文件内容"""
        
        if filename == 'main.py':
            return f'''#!/usr/bin/env python3
"""
{spec.get('name', 'Project')} - v1.0.0
{spec.get('description', '')}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
模板：CLI 工具
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
        
        elif filename == 'test_main.py':
            return f'''#!/usr/bin/env python3
"""
单元测试 - {spec.get('name', 'Project')}
"""

import unittest


class TestMain(unittest.TestCase):
    """测试主功能"""
    
    def test_import(self):
        """测试导入"""
        try:
            import sys
            sys.path.insert(0, 'src')
            # 这里导入主模块
            pass
        except Exception as e:
            self.fail(f"导入失败：{{e}}")
    
    def test_main_function(self):
        """测试主函数"""
        # TODO: 实现测试逻辑
        self.assertTrue(True)
    
    def test_edge_cases(self):
        """测试边界情况"""
        # TODO: 添加边界测试
        pass


if __name__ == "__main__":
    unittest.main()
'''
        
        elif filename == 'README.md':
            return f'''# {spec.get('name', 'Project')}

## 📋 简介

{spec.get('description', '项目描述')}

## ✨ 功能特性

- 功能 1
- 功能 2
- 功能 3

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python src/main.py --help
```

## 📖 使用说明

```bash
python src/main.py input [-o output] [-v]
```

## 🧪 测试

```bash
python -m pytest tests/ -v
```

## 📄 许可证

MIT License

---

**版本**: 1.0.0  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        elif filename == 'requirements.txt':
            return f'''# {spec.get('name', 'Project')} dependencies
# 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 核心依赖
# TODO: 根据实际需求添加

# 开发依赖
# pytest>=7.0.0
# black>=22.0.0
# flake8>=4.0.0
'''
        
        elif filename == 'config.py':
            name = spec.get('name', 'Project')
            return '''#!/usr/bin/env python3
"""
配置模块 - ''' + name + '''
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config:
    DEBUG = False
    VERSION = "1.0.0"
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "logs"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
'''
        
        return ''


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python template_engine.py <spec_file> [output_dir]")
        sys.exit(1)
    
    spec_file = Path(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else str(spec_file.parent)
    
    if not spec_file.exists():
        print(f"错误：文件不存在 {spec_file}")
        sys.exit(1)
    
    # 读取说明书
    with open(spec_file, 'r', encoding='utf-8') as f:
        spec_text = f.read()
    
    # 解析说明书
    spec = {
        'name': spec_file.parent.name,
        'description': '项目描述',
        'spec_text': spec_text
    }
    
    # 提取项目名称
    if '任务名称' in spec_text:
        spec['name'] = spec_text.split('任务名称')[1].split('\n')[1].strip()
    
    # 提取项目描述
    if '任务描述' in spec_text:
        spec['description'] = spec_text.split('任务描述')[1].split('\n')[1].strip()
    
    # 创建模板引擎
    engine = ProjectTemplateEngine()
    
    # 选择模板
    template_name = engine.select_template(spec_text)
    
    # 应用模板
    created_files = engine.apply_template(template_name, output_dir, spec)
    
    print(f"\n✅ 模板应用完成 - 创建 {len(created_files)} 个文件")


if __name__ == '__main__':
    main()
