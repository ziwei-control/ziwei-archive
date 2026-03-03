#!/usr/bin/env python3
# =============================================================================
# 知识图谱推理引擎
# 功能：构建知识图谱 + 图推理 + 知识发现
# =============================================================================

import json
import networkx as nx
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

Ziwei_DIR = Path("/home/admin/Ziwei")
KNOWLEDGE_DIR = Ziwei_DIR / "docs" / "knowledge"


class KnowledgeGraph:
    """知识图谱引擎"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities = {}
        self.relations = []
    
    def build_from_knowledge(self, knowledge_results: Dict) -> nx.DiGraph:
        """从知识检索结果构建图谱"""
        print("\n🕸️ 构建知识图谱...")
        
        # 添加节点
        node_count = 0
        
        # 本地知识节点
        for item in knowledge_results.get('local_knowledge', []):
            node_id = f"local:{item.get('source', '')}"
            self.graph.add_node(
                node_id,
                type='knowledge',
                agent=item.get('agent', ''),
                keyword=item.get('keyword', ''),
                size=item.get('size', 0)
            )
            node_count += 1
        
        # 网络资源节点
        for item in knowledge_results.get('web_search', []):
            node_id = f"web:{item.get('url', '')}"
            self.graph.add_node(
                node_id,
                type='web',
                keyword=item.get('keyword', ''),
                source=item.get('source', '')
            )
            node_count += 1
        
        # 代码资源节点
        for item in knowledge_results.get('code_search', []):
            node_id = f"code:{item.get('query', '')}"
            self.graph.add_node(
                node_id,
                type='code',
                keyword=item.get('keyword', ''),
                platform=item.get('platform', '')
            )
            node_count += 1
        
        # 任务节点
        for item in knowledge_results.get('similar_tasks', []):
            node_id = f"task:{item.get('task_id', '')}"
            self.graph.add_node(
                node_id,
                type='task',
                task_type=item.get('type', '')
            )
            node_count += 1
        
        print(f"   添加 {node_count} 个节点")
        
        # 添加边（关联）
        edge_count = 0
        
        # 按关键词关联
        keywords_nodes = {}
        for node, data in self.graph.nodes(data=True):
            keyword = data.get('keyword', '')
            if keyword:
                if keyword not in keywords_nodes:
                    keywords_nodes[keyword] = []
                keywords_nodes[keyword].append(node)
        
        # 同一关键词的节点互相关联
        for keyword, nodes in keywords_nodes.items():
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i+1:]:
                    self.graph.add_edge(
                        node1, node2,
                        relation='same_keyword',
                        keyword=keyword
                    )
                    edge_count += 1
        
        # 按类型关联
        type_nodes = {}
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('type', '')
            if node_type:
                if node_type not in type_nodes:
                    type_nodes[node_type] = []
                type_nodes[node_type].append(node)
        
        # 同类型节点关联
        for node_type, nodes in type_nodes.items():
            if len(nodes) > 1:
                for i, node1 in enumerate(nodes):
                    for node2 in nodes[i+1:]:
                        self.graph.add_edge(
                            node1, node2,
                            relation='same_type',
                            type=node_type
                        )
                        edge_count += 1
        
        print(f"   添加 {edge_count} 条边")
        
        return self.graph
    
    def infer_new_knowledge(self) -> List[Dict]:
        """图推理：发现新知识"""
        print("\n🧠 图推理...")
        
        inferences = []
        
        # 1. 传递性推理
        for node1 in self.graph.nodes():
            for node2 in self.graph.successors(node1):
                for node3 in self.graph.successors(node2):
                    if node1 != node3 and not self.graph.has_edge(node1, node3):
                        # 发现潜在的间接关联
                        inferences.append({
                            'type': 'transitive',
                            'from': node1,
                            'to': node3,
                            'via': node2,
                            'confidence': 0.7
                        })
        
        print(f"   发现 {len(inferences)} 个传递关系")
        
        # 2. 社区发现
        try:
            communities = list(nx.community.greedy_modularity_communities(self.graph.to_undirected()))
            
            for i, community in enumerate(communities[:5]):  # 前 5 个社区
                if len(community) > 2:
                    inferences.append({
                        'type': 'community',
                        'id': i,
                        'nodes': list(community),
                        'size': len(community),
                        'confidence': 0.8
                    })
            
            print(f"   发现 {len(communities)} 个知识社区")
        except:
            pass
        
        # 3. 中心节点识别
        try:
            centrality = nx.degree_centrality(self.graph)
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for node, score in top_nodes:
                if score > 0.1:  # 高度节点
                    inferences.append({
                        'type': 'hub',
                        'node': node,
                        'centrality': score,
                        'confidence': 0.9
                    })
            
            print(f"   识别 {len(top_nodes)} 个中心节点")
        except:
            pass
        
        return inferences
    
    def query_similar(self, query_keywords: List[str]) -> List[Dict]:
        """查询相似知识"""
        results = []
        
        for keyword in query_keywords:
            # 查找包含该关键词的节点
            for node, data in self.graph.nodes(data=True):
                if data.get('keyword', '').lower() == keyword.lower():
                    # 获取邻居节点
                    neighbors = list(self.graph.neighbors(node))
                    
                    results.append({
                        'query': keyword,
                        'node': node,
                        'data': data,
                        'neighbors': neighbors[:10],  # 最多 10 个邻居
                        'neighbor_count': len(neighbors)
                    })
        
        return results
    
    def visualize(self, output_file: str = None):
        """可视化知识图谱（简化版）"""
        print("\n📊 图谱统计:")
        print(f"   节点数：{self.graph.number_of_nodes()}")
        print(f"   边数：{self.graph.number_of_edges()}")
        print(f"   密度：{nx.density(self.graph):.4f}")
        
        try:
            print(f"   平均度：{sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes():.2f}")
        except:
            pass
        
        # 保存图谱数据
        if output_file:
            data = {
                'nodes': [
                    {'id': n, **d} 
                    for n, d in self.graph.nodes(data=True)
                ],
                'edges': [
                    {'source': s, 'target': t, **d}
                    for s, t, d in self.graph.edges(data=True)
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 图谱已保存：{output_file}")


def main():
    """主函数"""
    # 示例
    kg = KnowledgeGraph()
    
    # 模拟知识检索结果
    mock_results = {
        'local_knowledge': [
            {'source': 'T-01/file1.md', 'agent': 'T-01', 'keyword': 'python', 'size': 1000},
            {'source': 'T-02/file2.md', 'agent': 'T-02', 'keyword': 'python', 'size': 2000},
        ],
        'web_search': [
            {'url': 'https://python.org', 'keyword': 'python', 'source': 'Google'},
        ],
        'code_search': [
            {'query': 'python file', 'keyword': 'python', 'platform': 'GitHub'},
        ],
        'similar_tasks': []
    }
    
    # 构建图谱
    graph = kg.build_from_knowledge(mock_results)
    
    # 推理
    inferences = kg.infer_new_knowledge()
    
    # 查询
    results = kg.query_similar(['python'])
    
    # 可视化
    kg.visualize('/home/admin/Ziwei/data/knowledge_graph.json')


if __name__ == '__main__':
    main()
