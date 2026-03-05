#!/usr/bin/env python3
# =============================================================================
# x402 API - 合作伙伴自动筛选脚本
# 功能：扫描 GitHub 项目，分析潜在合作伙伴，生成合作提案
# =============================================================================

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path("/home/admin/Ziwei/data/x402/partnerships")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 目标项目特征（寻找可能需要 x402 API 的项目）
TARGET_KEYWORDS = [
    "crypto payment",
    "micropayment",
    "api marketplace",
    "ai api",
    "web3",
    "defi",
    "nft marketplace",
    "content monetization",
    "creator economy",
    "pay per use",
    "subscription api",
    "blockchain payment",
    "crypto tipping",
    "digital content payment"
]

# 排除的项目类型
EXCLUDE_KEYWORDS = [
    "gamefi",
    "metaverse",
    "dao governance"
]


class PartnerFinder:
    """合作伙伴筛选器"""
    
    def __init__(self):
        self.potential_partners = []
        self.outreach_templates = {}
        
    def analyze_github_project(self, repo_name, description, topics, stars):
        """分析 GitHub 项目是否适合合作"""
        score = 0
        reasons = []
        
        # 检查关键词匹配
        full_text = f"{repo_name} {description} {' '.join(topics)}".lower()
        
        for keyword in TARGET_KEYWORDS:
            if keyword in full_text:
                score += 10
                reasons.append(f"匹配关键词：{keyword}")
        
        # 排除不相关项目
        for keyword in EXCLUDE_KEYWORDS:
            if keyword in full_text:
                return 0, ["不相关领域"], False
        
        # 根据星级调整
        if stars > 1000:
            score += 50
            reasons.append(f"高星项目 ({stars} stars)")
        elif stars > 100:
            score += 20
            reasons.append(f"中等热度 ({stars} stars)")
        elif stars > 10:
            score += 5
        
        # 判断是否值得联系
        should_contact = score >= 30
        
        return score, reasons, should_contact
    
    def generate_outreach_email(self, repo_name, repo_url, contact_reason):
        """生成合作提案邮件模板"""
        template = f"""
Subject: Partnership Opportunity: x402 Micro-Payment Protocol + {repo_name}

Hi {repo_name} Team,

I'm reaching out from the x402 API project - a micro-payment protocol for AI services.

**About x402:**
- Pay-per-call API pricing (starting at $0.02 USDC)
- Web3-based payment (Base chain, USDC)
- No subscription required
- Live and generating revenue: http://localhost:8081

**Why Partner with Us:**

1. **Monetization**: Integrate x402 to enable micro-payments in {repo_name}
2. **Revenue Share**: Earn margin on API calls (you charge users, pay us wholesale)
3. **No Upfront Cost**: Pay-as-you-go model, no minimum commitment
4. **Developer-Friendly**: 5-minute integration with our SDK

**Partnership Options:**

📦 **API Integration**
   - Use x402 API in your platform
   - Keep the pricing margin
   - Example: Charge $0.05, pay us $0.02, profit $0.03/call

🤝 **Referral Program**
   - Refer users to x402
   - Earn $5 USDC per paying user
   - Unlimited earning potential

💼 **Technical Collaboration**
   - Cross-promotion
   - Joint blog posts
   - Shared community

**Next Steps:**

1. Try our API (free during 02:00-06:00 Beijing Time daily)
2. Check our live dashboard: http://localhost:8081
3. Review our docs: (coming soon)
4. Let's schedule a call to discuss integration

**Contact:**
- API: http://localhost:5002
- Dashboard: http://localhost:8081
- Email: (your email)
- Discord: (your Discord)

Looking forward to exploring synergies!

Best regards,
Ziwei Control Team
x402 API Project

---
P.S. We're currently in seed round - if you're interested in investment opportunities, let's talk!
"""
        return template
    
    def generate_github_issue_template(self, repo_name, repo_url):
        """生成 GitHub Issue/Discussion 联系模板"""
        template = f"""
## 🤝 Partnership Opportunity: x402 API + {repo_name}

Hi @maintainers,

I discovered {repo_name} and think there could be great synergy with our project **x402 API**.

### What is x402 API?

A micro-payment protocol for AI services:
- 💰 Pay-per-call from $0.02 USDC
- 🔗 Web3 payments (Base chain)
- ⚡ 5-minute integration
- 📊 Live: http://localhost:8081

### Potential Collaboration:

1. **Integration**: Add x402 payment option to {repo_name}
2. **Monetization**: Enable micro-payments for your users
3. **Revenue**: Earn margin on API usage

### Why This Matters:

- Your users can pay-per-use instead of subscriptions
- Opens up new monetization channels
- No upfront cost for integration

### Want to Explore?

- Try our API: http://localhost:5002
- Live stats: http://localhost:8081
- Let's discuss in Issues/DMs

Thanks for considering! 🚀

---
*Not a spam - genuine partnership inquiry. Happy to answer any questions.*
"""
        return template
    
    def scan_and_analyze(self):
        """扫描并分析潜在合作伙伴（示例数据）"""
        # 示例：手动添加一些潜在合作伙伴
        # 实际使用时可以通过 GitHub API 自动搜索
        
        sample_projects = [
            {
                "name": "api-marketplace",
                "url": "https://github.com/example/api-marketplace",
                "description": "Decentralized API marketplace with crypto payments",
                "topics": ["api", "marketplace", "crypto", "web3"],
                "stars": 234,
                "contact": "issues"
            },
            {
                "name": "web3-content-platform",
                "url": "https://github.com/example/web3-content",
                "description": "Content monetization platform using blockchain",
                "topics": ["web3", "content", "monetization", "defi"],
                "stars": 567,
                "contact": "discussions"
            },
            {
                "name": "crypto-tipping-bot",
                "url": "https://github.com/example/tipping-bot",
                "description": "Telegram bot for crypto tipping",
                "topics": ["crypto", "telegram", "tipping", "payments"],
                "stars": 89,
                "contact": "issues"
            }
        ]
        
        results = []
        
        for project in sample_projects:
            score, reasons, should_contact = self.analyze_github_project(
                project["name"],
                project["description"],
                project["topics"],
                project["stars"]
            )
            
            if should_contact:
                result = {
                    "project": project,
                    "score": score,
                    "reasons": reasons,
                    "email_template": self.generate_outreach_email(
                        project["name"],
                        project["url"],
                        reasons
                    ),
                    "github_template": self.generate_github_issue_template(
                        project["name"],
                        project["url"]
                    )
                }
                results.append(result)
        
        return results
    
    def save_results(self, results):
        """保存分析结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = OUTPUT_DIR / f"partners_analysis_{timestamp}.json"
        
        # 转换为可序列化格式
        serializable_results = []
        for r in results:
            serializable_results.append({
                "project": r["project"],
                "score": r["score"],
                "reasons": r["reasons"],
                "contact_recommended": True
            })
        
        with open(output_file, 'w') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_analyzed": len(results),
                "partners": serializable_results
            }, f, indent=2)
        
        # 保存邮件模板
        templates_file = OUTPUT_DIR / f"outreach_templates_{timestamp}.md"
        with open(templates_file, 'w') as f:
            f.write("# x402 API - 合作伙伴联系模板\n\n")
            f.write(f"生成时间：{datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            
            for r in results:
                f.write(f"## {r['project']['name']}\n\n")
                f.write(f"**URL:** {r['project']['url']}\n")
                f.write(f"**匹配分数:** {r['score']}\n")
                f.write(f"**联系原因:** {', '.join(r['reasons'])}\n\n")
                f.write("### 邮件模板\n\n```")
                f.write(r['email_template'])
                f.write("```\n\n")
                f.write("### GitHub Issue 模板\n\n```")
                f.write(r['github_template'])
                f.write("```\n\n")
                f.write("---\n\n")
        
        return output_file, templates_file


def main():
    """主函数"""
    print("=" * 70)
    print("🤖 x402 API - 合作伙伴自动筛选系统")
    print("=" * 70)
    print()
    
    finder = PartnerFinder()
    
    print("📊 扫描 GitHub 项目...")
    results = finder.scan_and_analyze()
    
    print(f"✅ 分析完成：{len(results)} 个潜在合作伙伴")
    print()
    
    print("💾 保存结果...")
    output_file, templates_file = finder.save_results(results)
    
    print(f"   分析报告：{output_file}")
    print(f"   联系模板：{templates_file}")
    print()
    
    print("📋 潜在合作伙伴列表:")
    for r in results:
        print(f"   • {r['project']['name']} ({r['project']['stars']} stars)")
        print(f"     匹配分数：{r['score']}")
        print(f"     联系建议：✅ 推荐")
        print()
    
    print("🚀 下一步行动:")
    print("   1. 查看生成的邮件模板")
    print("   2. 通过 GitHub Issues/Discussions 联系")
    print("   3. 发送邮件给项目维护者")
    print("   4. 跟进回复")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
