#!/usr/bin/env python3
# =============================================================================
# 紫微智控 Agent 包装器 - x402 API
# 功能：将紫微智控的 8 个 Agent 包装为 API 调用
# =============================================================================

import requests
import json
from typing import Dict, Optional

# 阿里百炼 API 配置
DASHSCOPE_API_KEY = "sk-sp-..."  # 需要从 .env 加载
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

class ZiweiAgent:
    """紫微智控 Agent 基类"""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.api_key = DASHSCOPE_API_KEY

    def call(self, prompt: str, **kwargs) -> Optional[Dict]:
        """调用阿里百炼 API"""
        try:
            url = f"{DASHSCOPE_BASE_URL}/services/aigc/text-generation/generation"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model_id,
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", 2000),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if "output" in data and "text" in data["output"]:
                    return {
                        "result": data["output"]["text"],
                        "model": self.model_id,
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
            else:
                return {"error": f"API 调用失败: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

        return None


# 8 个 Agent 类
class ArchitectAgent(ZiweiAgent):
    """T-01 首席架构师 - 架构设计"""
    def __init__(self):
        super().__init__("bailian/qwen3-max-2026-01-23")

    def design(self, requirements: str) -> Optional[Dict]:
        prompt = f"""作为系统架构师，请根据以下需求设计技术架构：

需求：
{requirements}

请提供：
1. 技术栈选择
2. 系统架构图（文字描述）
3. 数据库设计
4. API 设计
5. 部署方案

要求：详细、专业、可落地。"""
        return self.call(prompt)


class CodeGenAgent(ZiweiAgent):
    """T-02 代码特种兵 - 代码生成"""
    def __init__(self):
        super().__init__("bailian/qwen3-coder-plus")

    def generate(self, language: str, description: str) -> Optional[Dict]:
        prompt = f"""使用 {language} 编写代码实现以下功能：

{description}

要求：
1. 代码规范，有注释
2. 包含错误处理
3. 提供完整可运行的代码
4. 如果需要依赖，说明安装方法"""
        return self.call(prompt)


class CodeAuditAgent(ZiweiAgent):
    """T-03 代码审计员 - 代码审计"""
    def __init__(self):
        super().__init__("bailian/qwen3-coder-next")

    def audit(self, code: str, language: str = "Python") -> Optional[Dict]:
        prompt = f"""作为安全审计专家，审计以下 {language} 代码：

```{language.lower()}
{code}
```

请检查：
1. 安全漏洞（SQL注入、XSS、CSRF等）
2. 性能问题
3. 代码规范
4. 最佳实践
5. 修复建议

格式：使用列表列出问题和建议。"""
        return self.call(prompt)


class LogicAgent(ZiweiAgent):
    """T-04 逻辑推理机 - 逻辑推理"""
    def __init__(self):
        super().__init__("bailian/qwen3.5-plus")

    def reason(self, problem: str) -> Optional[Dict]:
        prompt = f"""使用逻辑推理分析以下问题：

{problem}

请提供：
1. 问题分析
2. 逻辑推理过程
3. 结论
4. 假设和局限性"""
        return self.call(prompt)


class TranslateAgent(ZiweiAgent):
    """T-05 跨域翻译家 - 翻译"""
    def __init__(self):
        super().__init__("bailian/glm-4.7")

    def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        prompt = f"""将以下文本从 {source_lang} 翻译为 {target_lang}：

原文：
{text}

要求：
1. 准确翻译
2. 保持原文语气和风格
3. 专业术语翻译准确"""
        return self.call(prompt)


class LongTextAgent(ZiweiAgent):
    """T-06 长文解析器 - 长文本处理"""
    def __init__(self):
        super().__init__("bailian/kimi-k2.5")

    def analyze(self, long_text: str, task: str = "summary") -> Optional[Dict]:
        prompt = f"""分析以下长文本：

文本：
{long_text}

任务：{task}

请提供详细的分析结果。"""
        return self.call(prompt)


class CrawlAgent(ZiweiAgent):
    """T-07 网络爬虫 - 网络爬虫"""
    def __init__(self):
        super().__init__("qwen-portal/coder-model")

    def crawl(self, url: str, task: str = "extract") -> Optional[Dict]:
        prompt = f"""设计网络爬虫脚本访问以下 URL：

URL: {url}

任务：{task}

请提供：
1. 爬虫策略
2. Python 代码
3. 数据提取方案

注意：遵守 robots.txt 和反爬虫策略。"""
        return self.call(prompt)


class VisionAgent(ZiweiAgent):
    """V-01 视觉侦察兵 - 视觉解析"""
    def __init__(self):
        super().__init__("qwen-portal/vision-model")

    def analyze(self, image_url: str, task: str = "describe") -> Optional[Dict]:
        prompt = f"""分析以下图片：

图片 URL: {image_url}

任务：{task}

请提供详细的图片分析。"""
        return self.call(prompt)


# Agent 工厂
class AgentFactory:
    """Agent 工厂类"""

    _agents = {
        "architect": ArchitectAgent,
        "code-gen": CodeGenAgent,
        "code-audit": CodeAuditAgent,
        "logic": LogicAgent,
        "translate": TranslateAgent,
        "long-text": LongTextAgent,
        "crawl": CrawlAgent,
        "vision": VisionAgent
    }

    @classmethod
    def get_agent(cls, agent_type: str) -> Optional[ZiweiAgent]:
        """获取指定类型的 Agent"""
        if agent_type in cls._agents:
            return cls._agents[agent_type]()
        return None

    @classmethod
    def get_price(cls, agent_type: str) -> float:
        """获取 Agent 调用价格"""
        prices = {
            "architect": 0.10,
            "code-gen": 0.08,
            "code-audit": 0.05,
            "logic": 0.06,
            "translate": 0.02,
            "long-text": 0.03,
            "crawl": 0.04,
            "vision": 0.15
        }
        return prices.get(agent_type, 0.05)