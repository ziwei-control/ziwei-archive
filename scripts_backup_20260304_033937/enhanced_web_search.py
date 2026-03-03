#!/usr/bin/env python3
# =============================================================================
# 增强版网络搜索工具
# 功能：Brave Search API + 无头浏览器 + 多引擎搜索
# =============================================================================

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 配置
SEARCH_CONFIG = {
    'brave_api_key': os.getenv('BRAVE_API_KEY', ''),  # 如果有配置就用
    'timeout': 10,
    'max_results': 10,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


class EnhancedWebSearch:
    """增强版网络搜索"""
    
    def __init__(self):
        self.results = []
        self.search_engines = {
            'brave': self.search_brave,
            'google': self.search_google,
            'github': self.search_github,
            'stackoverflow': self.search_stackoverflow,
            'twitter': self.search_twitter,
            'pypi': self.search_pypi
        }
    
    def search_brave(self, query: str, count: int = 10) -> List[Dict]:
        """Brave Search API"""
        if not SEARCH_CONFIG['brave_api_key']:
            print("   ⚠️ Brave API 未配置，跳过")
            return []
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                'X-Subscription-Token': SEARCH_CONFIG['brave_api_key'],
                'Accept': 'application/json'
            }
            params = {
                'q': query,
                'count': min(count, 20),
                'text_decorations': True,
                'search_lang': 'en'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=SEARCH_CONFIG['timeout'])
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('web', {}).get('results', [])[:count]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'snippet': item.get('description', ''),
                        'source': 'Brave Search',
                        'timestamp': datetime.now().isoformat()
                    })
                
                print(f"   ✅ Brave Search: {len(results)} 个结果")
                return results
            else:
                print(f"   ⚠️ Brave API 错误：{response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ⚠️ Brave Search 失败：{e}")
            return []
    
    def search_google(self, query: str, count: int = 10) -> List[Dict]:
        """Google 搜索（无头浏览器）"""
        try:
            # 使用 Google Custom Search API 或 无头浏览器
            # 这里使用 Google Custom Search（如果有 API key）
            api_key = os.getenv('GOOGLE_API_KEY', '')
            cx = os.getenv('GOOGLE_CX', '')
            
            if api_key and cx:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': api_key,
                    'cx': cx,
                    'q': query,
                    'num': min(count, 10)
                }
                
                response = requests.get(url, params=params, timeout=SEARCH_CONFIG['timeout'])
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data.get('items', [])[:count]:
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('link', ''),
                            'snippet': item.get('snippet', ''),
                            'source': 'Google',
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    print(f"   ✅ Google: {len(results)} 个结果")
                    return results
            
            # 降级方案：返回推荐链接
            print(f"   ⚠️ Google API 未配置，使用推荐链接")
            return self._generate_google_links(query, count)
            
        except Exception as e:
            print(f"   ⚠️ Google 搜索失败：{e}")
            return self._generate_google_links(query, count)
    
    def _generate_google_links(self, query: str, count: int) -> List[Dict]:
        """生成 Google 搜索推荐链接"""
        encoded_query = query.replace(' ', '+')
        results = []
        
        # 生成相关搜索链接
        sites = [
            f"https://www.google.com/search?q={encoded_query}+python+tutorial",
            f"https://docs.python.org/3/search.html?q={encoded_query}",
            f"https://stackoverflow.com/questions/tagged/{encoded_query.replace('+', '-')}",
            f"https://github.com/search?q={encoded_query}+python",
            f"https://pypi.org/search/?q={encoded_query}",
            f"https://realpython.com/search?q={encoded_query}",
            f"https://medium.com/search?q={encoded_query}+python",
            f"https://www.reddit.com/search?q={encoded_query}+python"
        ]
        
        for i, url in enumerate(sites[:count]):
            results.append({
                'title': f'{query} - 相关资源 {i+1}',
                'url': url,
                'snippet': f'搜索：{query}',
                'source': 'Google (推荐)',
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def search_github(self, query: str, count: int = 10) -> List[Dict]:
        """GitHub 代码搜索"""
        try:
            # GitHub API
            token = os.getenv('GITHUB_TOKEN', '')
            headers = {'Authorization': f'token {token}'} if token else {}
            
            url = f"https://api.github.com/search/code?q={query}+language:python&per_page={count}"
            response = requests.get(url, headers=headers, timeout=SEARCH_CONFIG['timeout'])
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', [])[:count]:
                    results.append({
                        'title': f"{item.get('name', '')} - {item.get('path', '')}",
                        'url': item.get('html_url', ''),
                        'snippet': f"Repository: {item.get('repository', {}).get('full_name', '')}",
                        'source': 'GitHub',
                        'timestamp': datetime.now().isoformat()
                    })
                
                print(f"   ✅ GitHub: {len(results)} 个代码资源")
                return results
            else:
                print(f"   ⚠️ GitHub API 错误：{response.status_code}")
                return self._generate_github_links(query, count)
                
        except Exception as e:
            print(f"   ⚠️ GitHub 搜索失败：{e}")
            return self._generate_github_links(query, count)
    
    def _generate_github_links(self, query: str, count: int) -> List[Dict]:
        """生成 GitHub 推荐链接"""
        results = []
        encoded_query = query.replace(' ', '+')
        
        links = [
            f"https://github.com/search?q={encoded_query}+language:python",
            f"https://github.com/topics/{query.lower().replace(' ', '-')}",
            f"https://github.com/trending/python"
        ]
        
        for i, url in enumerate(links[:count]):
            results.append({
                'title': f'GitHub - {query}',
                'url': url,
                'snippet': f'搜索：{query} Python 项目',
                'source': 'GitHub (推荐)',
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def search_stackoverflow(self, query: str, count: int = 10) -> List[Dict]:
        """Stack Overflow 搜索"""
        try:
            url = f"https://api.stackexchange.com/2.3/search"
            params = {
                'site': 'stackoverflow',
                'q': query,
                'pagesize': min(count, 30)
            }
            
            response = requests.get(url, params=params, timeout=SEARCH_CONFIG['timeout'])
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', [])[:count]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('tags', []),
                        'source': 'Stack Overflow',
                        'timestamp': datetime.now().isoformat()
                    })
                
                print(f"   ✅ Stack Overflow: {len(results)} 个问题")
                return results
                
        except Exception as e:
            print(f"   ⚠️ Stack Overflow 搜索失败：{e}")
        
        return self._generate_stackoverflow_links(query, count)
    
    def _generate_stackoverflow_links(self, query: str, count: int) -> List[Dict]:
        """生成 Stack Overflow 推荐链接"""
        encoded_query = query.replace(' ', '+')
        return [{
            'title': f'{query} - Stack Overflow',
            'url': f"https://stackoverflow.com/questions/tagged/{encoded_query.replace('+', '-')}",
            'snippet': f'搜索：{query}',
            'source': 'Stack Overflow (推荐)',
            'timestamp': datetime.now().isoformat()
        }]
    
    def search_twitter(self, query: str, count: int = 10) -> List[Dict]:
        """Twitter 搜索（需要 API）"""
        print(f"   ⚠️ Twitter API 需要认证，使用推荐链接")
        return self._generate_twitter_links(query, count)
    
    def _generate_twitter_links(self, query: str, count: int) -> List[Dict]:
        """生成 Twitter 推荐链接"""
        encoded_query = query.replace(' ', '+')
        return [{
            'title': f'{query} - Twitter',
            'url': f"https://twitter.com/search?q={encoded_query}",
            'snippet': f'搜索：{query}',
            'source': 'Twitter (推荐)',
            'timestamp': datetime.now().isoformat()
        }]
    
    def search_pypi(self, query: str, count: int = 10) -> List[Dict]:
        """PyPI 包搜索"""
        try:
            url = f"https://pypi.org/search/?q={query}"
            response = requests.get(url, timeout=SEARCH_CONFIG['timeout'])
            
            if response.status_code == 200:
                # 简单解析
                results = [{
                    'title': f'{query} - PyPI',
                    'url': url,
                    'snippet': f'搜索 Python 包：{query}',
                    'source': 'PyPI',
                    'timestamp': datetime.now().isoformat()
                }]
                
                print(f"   ✅ PyPI: 1 个搜索结果页面")
                return results
                
        except Exception as e:
            print(f"   ⚠️ PyPI 搜索失败：{e}")
        
        return []
    
    def search(self, query: str, engines: List[str] = None, count: int = 10) -> List[Dict]:
        """执行多引擎搜索"""
        print(f"\n🔍 搜索：{query}")
        
        if engines is None:
            engines = ['brave', 'google', 'github', 'stackoverflow']
        
        all_results = []
        
        for engine in engines:
            if engine in self.search_engines:
                results = self.search_engines[engine](query, count)
                all_results.extend(results)
                time.sleep(0.5)  # 避免请求过快
        
        # 去重
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        print(f"\n📊 总计：{len(unique_results)} 个唯一结果")
        return unique_results


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python enhanced_web_search.py <query> [engines]")
        print("示例：python enhanced_web_search.py 'python file handling'")
        sys.exit(1)
    
    query = sys.argv[1]
    engines = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    
    searcher = EnhancedWebSearch()
    results = searcher.search(query, engines)
    
    # 保存结果
    output_file = Path(f"web_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'query': query, 'results': results}, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 结果已保存：{output_file}")


if __name__ == '__main__':
    main()
