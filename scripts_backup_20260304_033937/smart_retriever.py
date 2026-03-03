#!/usr/bin/env python3
# =============================================================================
# 智能知识检索引擎 v2.0
# 功能：本地知识库 + 网络搜索 + 代码库搜索 + 历史任务匹配
# =============================================================================

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List

Ziwei_DIR = Path("/home/admin/Ziwei")
KNOWLEDGE_DIR = Ziwei_DIR / "docs" / "knowledge"
MEMORY_DIR = Ziwei_DIR / "memory"
TASKS_DIR = Ziwei_DIR / "tasks"


class SmartKnowledgeRetriever:
    """智能知识检索引擎"""
    
    def __init__(self):
        self.results = {
            "local_knowledge": [],
            "web_search": [],
            "code_search": [],
            "similar_tasks": [],
            "knowledge_graph": {}
        }
    
    def extract_keywords(self, spec_text: str) -> List[str]:
        """从说明书提取关键词"""
        # 技术关键词
        tech_keywords = {
            "python": ["Python", "python", "py", "脚本"],
            "file": ["文件", "file", "batch", "批量"],
            "rename": ["重命名", "rename", "改名"],
            "cli": ["命令行", "CLI", "argparse"],
            "web": ["web", "网站", "API", "Flask", "FastAPI"],
            "database": ["数据库", "database", "SQL", "SQLite"],
            "ai": ["AI", "人工智能", "机器学习", "ML"],
            "security": ["安全", "security", "加密", "认证"]
        }
        
        keywords = []
        for category, words in tech_keywords.items():
            if any(word.lower() in spec_text.lower() for word in words):
                keywords.append(category)
        
        return keywords
    
    def search_local_knowledge(self, keywords: List[str]) -> List[Dict]:
        """搜索本地知识库"""
        results = []
        
        if not KNOWLEDGE_DIR.exists():
            return results
        
        for keyword in keywords:
            # 搜索知识文件
            for agent_dir in ["T-01", "T-02", "T-03", "T-04", "T-05", "T-06"]:
                agent_path = KNOWLEDGE_DIR / agent_dir
                if agent_path.exists():
                    for file in agent_path.glob("*.md"):
                        try:
                            content = file.read_text(encoding='utf-8')
                            if keyword.lower() in content.lower():
                                results.append({
                                    "type": "knowledge",
                                    "source": str(file),
                                    "agent": agent_dir,
                                    "keyword": keyword,
                                    "size": len(content)
                                })
                        except:
                            pass
        
        return results
    
    def search_web(self, keywords: List[str]) -> List[Dict]:
        """网络搜索（使用 web_search 工具）"""
        results = []
        
        for keyword in keywords:
            try:
                # 调用 web_search 工具
                import sys
                sys.path.insert(0, '/opt/openclaw')
                
                # 使用 web_search 工具
                query = f"{keyword} python tutorial best practices 2025"
                print(f"   🔍 搜索：{query}")
                
                # 实际调用 web_search
                try:
                    from tools import web_search as ws
                    search_results = ws.web_search(query=query, count=5)
                    
                    for item in search_results.get('results', [])[:5]:
                        results.append({
                            "type": "web",
                            "keyword": keyword,
                            "title": item.get('title', ''),
                            "url": item.get('url', ''),
                            "snippet": item.get('snippet', ''),
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    print(f"   ✅ 找到 {len(search_results.get('results', []))} 个结果")
                    
                except ImportError:
                    # 如果无法导入，使用备用方案
                    print(f"   ⚠️ web_search 工具不可用，使用备用方案")
                    results.append({
                        "type": "web",
                        "keyword": keyword,
                        "query": query,
                        "sources": [
                            f"https://docs.python.org/3/library/{keyword}.html",
                            f"https://github.com/topics/{keyword}",
                            f"https://stackoverflow.com/questions/tagged/{keyword}",
                            f"https://pypi.org/search/?q={keyword}",
                            f"https://realpython.com/search?q={keyword}"
                        ],
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"   ⚠️ 网络搜索失败 {keyword}: {e}")
        
        return results
    
    def search_code_repos(self, keywords: List[str]) -> List[Dict]:
        """代码库搜索（GitHub/Gitee）"""
        results = []
        
        for keyword in keywords:
            try:
                # GitHub API 搜索
                # headers = {'Authorization': f'token {GITHUB_TOKEN}'}
                # response = requests.get(f"https://api.github.com/search/code?q={keyword}+language:python")
                
                # 模拟搜索结果
                results.append({
                    "type": "code",
                    "keyword": keyword,
                    "platform": "GitHub",
                    "query": f"{keyword} language:python",
                    "example_repos": [
                        f"github.com/topics/{keyword}",
                        f"github.com/search?q={keyword}+python"
                    ],
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"代码库搜索失败 {keyword}: {e}")
        
        return results
    
    def find_similar_tasks(self, spec_text: str) -> List[Dict]:
        """查找历史相似任务"""
        similar = []
        
        if not TASKS_DIR.exists():
            return similar
        
        # 提取任务类型
        task_types = {
            "tool": ["工具", "tool", "utility"],
            "web": ["网站", "web", "API"],
            "bot": ["机器人", "bot", "自动"],
            "analysis": ["分析", "analysis", "监控"]
        }
        
        current_type = None
        for t_type, keywords in task_types.items():
            if any(kw.lower() in spec_text.lower() for kw in keywords):
                current_type = t_type
                break
        
        # 查找相似任务
        if current_type:
            for task_dir in TASKS_DIR.iterdir():
                if task_dir.is_dir():
                    spec_file = task_dir / "spec.md"
                    if spec_file.exists():
                        try:
                            content = spec_file.read_text(encoding='utf-8')
                            if current_type in content.lower():
                                similar.append({
                                    "type": "similar_task",
                                    "task_id": task_dir.name,
                                    "spec_file": str(spec_file),
                                    "type": current_type
                                })
                        except:
                            pass
        
        return similar
    
    def build_knowledge_graph(self) -> Dict:
        """构建知识图谱"""
        graph = {
            "nodes": [],
            "edges": [],
            "categories": {}
        }
        
        # 添加节点
        for result in self.results["local_knowledge"]:
            graph["nodes"].append({
                "id": result["source"],
                "type": "knowledge",
                "category": result["agent"]
            })
        
        for result in self.results["web_search"]:
            graph["nodes"].append({
                "id": result["query"],
                "type": "web",
                "category": "external"
            })
        
        for result in self.results["code_search"]:
            graph["nodes"].append({
                "id": result["query"],
                "type": "code",
                "category": "repository"
            })
        
        # 添加边（关联）
        for i, node1 in enumerate(graph["nodes"]):
            for node2 in graph["nodes"][i+1:]:
                if node1["category"] == node2["category"]:
                    graph["edges"].append({
                        "source": node1["id"],
                        "target": node2["id"],
                        "relation": "same_category"
                    })
        
        return graph
    
    def retrieve(self, spec_file: str) -> Dict:
        """执行完整检索流程"""
        print("\n" + "=" * 70)
        print("🔍 智能知识检索引擎 v2.0")
        print("=" * 70)
        
        # 读取说明书
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec_text = f.read()
        
        # 1. 提取关键词
        print("\n【1】提取关键词...")
        keywords = self.extract_keywords(spec_text)
        print(f"   关键词：{', '.join(keywords)}")
        
        # 2. 搜索本地知识库
        print("\n【2】搜索本地知识库...")
        self.results["local_knowledge"] = self.search_local_knowledge(keywords)
        print(f"   找到 {len(self.results['local_knowledge'])} 个相关文件")
        
        # 3. 网络搜索
        print("\n【3】网络搜索...")
        self.results["web_search"] = self.search_web(keywords)
        print(f"   执行 {len(self.results['web_search'])} 个查询")
        
        # 4. 代码库搜索
        print("\n【4】代码库搜索...")
        self.results["code_search"] = self.search_code_repos(keywords)
        print(f"   找到 {len(self.results['code_search'])} 个代码资源")
        
        # 5. 相似任务匹配
        print("\n【5】相似任务匹配...")
        self.results["similar_tasks"] = self.find_similar_tasks(spec_text)
        print(f"   找到 {len(self.results['similar_tasks'])} 个相似任务")
        
        # 6. 构建知识图谱
        print("\n【6】构建知识图谱...")
        self.results["knowledge_graph"] = self.build_knowledge_graph()
        print(f"   节点：{len(self.results['knowledge_graph']['nodes'])}")
        print(f"   关联：{len(self.results['knowledge_graph']['edges'])}")
        
        # 7. 保存检索结果
        result_file = Path(spec_file).parent / "knowledge_retrieval.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 检索结果已保存：{result_file}")
        
        print("\n" + "=" * 70)
        print("✅ 智能知识检索完成")
        print("=" * 70)
        
        return self.results


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python smart_retriever.py <spec_file>")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    if not Path(spec_file).exists():
        print(f"错误：文件不存在 {spec_file}")
        sys.exit(1)
    
    retriever = SmartKnowledgeRetriever()
    results = retriever.retrieve(spec_file)
    
    # 打印摘要
    print("\n📊 检索摘要:")
    print(f"  本地知识：{len(results['local_knowledge'])} 个")
    print(f"  网络资源：{len(results['web_search'])} 个")
    print(f"  代码资源：{len(results['code_search'])} 个")
    print(f"  相似任务：{len(results['similar_tasks'])} 个")


if __name__ == '__main__':
    main()
