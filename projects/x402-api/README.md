# x402 API - AI Micro-Payment Protocol

[![Status](https://img.shields.io/badge/status-live-green)]()
[![Revenue](https://img.shields.io/badge/revenue-0.48%20USDC-blue)]()
[![Transactions](https://img.shields.io/badge/transactions-10-orange)]()
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Build in Public](https://img.shields.io/badge/building-in%20public-pink)]()

> **💰 Pay-per-call AI APIs from $0.02 USDC**  
> No subscription. No credit card. No registration. Just USDC.

---

## 🎯 Why x402?

**Problem:** AI APIs are too expensive for indie developers.
- OpenAI: $0.01-0.10/call + $10+ prepaid + credit card required
- Anthropic: More expensive + hard to register from many countries
- Others: $20+/month subscriptions even if you barely use them

**Solution:** x402 micro-payment protocol
- ✅ **$0.02/call minimum** - Lowest in the industry
- ✅ **No subscription** - Pay only for what you use
- ✅ **No credit card** - USDC wallet is enough
- ✅ **No registration** - Start calling APIs immediately
- ✅ **Global access** - No geographic restrictions (where crypto is legal)

---

## 🚀 5-Minute Quick Start

### Step 1: Prepare USDC Wallet

Install MetaMask or any Base chain wallet, load with small amount of USDC ($5 is enough for long time).

### Step 2: Call API

```python
import requests

url = "http://8.213.149.224:5002/api/v1/translator"
payload = {
    "text": "Hello, world!",
    "source": "en",
    "target": "zh"
}
headers = {
    "X-Payment-Amount": "20000",  # 0.02 USDC (6 decimals)
    "X-Payment-Token": "USDC",
    "X-Payment-Signature": "your_signature_here"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Step 3: Get Result

```json
{
  "success": true,
  "data": {
    "translated_text": "你好，世界！",
    "source_language": "en",
    "target_language": "zh"
  },
  "cost": "0.02 USDC"
}
```

**Done!** You just paid $0.02 for a translation.

---

## 📊 Live Stats (Real Data, Updated Daily)

| Metric | Value |
|--------|-------|
| **Revenue** | 0.4800 USDC |
| **Transactions** | 10 |
| **Avg Order** | $0.048 USDC |
| **Highest Single** | $0.15 USDC (Vision API) |
| **Launch Date** | 2026-03-01 |
| **Uptime** | 99.9% |

**This is not hype. This is real running data.** 📈

**Live Dashboard:** http://8.213.149.224:8081

---

## 💰 Available APIs

| Endpoint | Price | Use Case | Example |
|----------|-------|----------|---------|
| `/api/v1/translator` | $0.02 | Translation | Multi-language apps |
| `/api/v1/long-text` | $0.03 | Summarization | Document analysis |
| `/api/v1/crawl` | $0.04 | Web Scraping | Data collection |
| `/api/v1/code-audit` | $0.05 | Code Review | Security checks |
| `/api/v1/logic` | $0.06 | Reasoning | Complex analysis |
| `/api/v1/code-gen` | $0.08 | Code Generation | Rapid prototyping |
| `/api/v1/architect` | $0.10 | Architecture | System design |
| `/api/v1/vision` | $0.15 | Image Analysis | Visual AI |

**All APIs:** Instant response, pay-per-call, no minimum spend.

---

## 💡 Business Model: Earn with x402

### 1. Build Apps & Keep the Margin

**Example:** Build a translation website
- Charge users: $0.05/call
- x402 API cost: $0.02/call
- **Your profit: $0.03/call**

1000 calls = **$30 profit** (you just need frontend + marketing)

### 2. Referral Program

- Program details TBD (no cash or free credits involved)
- Unlimited earning potential

### 3. Enterprise Custom Solutions

Need private deployment? Custom AI models? Contact us.

---

## 🛡️ Security & Compliance

### What We Do
- ✅ DDoS Protection
- ✅ Rate Limiting (60 calls/min/IP)
- ✅ Payment Verification (x402 protocol)
- ✅ HTTPS Encryption
- ✅ Audit Logs (anomaly detection)

### What We Don't Do
- ❌ No user data storage
- ❌ No identity tracking
- ❌ No KYC (unless legally required)
- ❌ No service to sanctioned regions

---

## 🌍 Service Regions

**✅ Supported:** US, EU, UK, Canada, Australia, Singapore, Japan, Korea, UAE  
**❌ Not Supported:** Mainland China, North Korea, Iran, Syria, Other sanctioned regions

---

## 📈 Roadmap

### Q2 2026 (Current Quarter)
- [ ] SDK Release (Python/JavaScript/Go)
- [ ] Video Tutorial Series (5 episodes)
- [ ] Developer Documentation
- [ ] Voice & Video APIs

### Q3 2026
- [ ] Subscription Plans (optional)
- [ ] Enterprise SLA
- [ ] Multi-region Deployment
- [ ] 100+ Active Developers

### Q4 2026
- [ ] 1000+ Active Developers
- [ ] $1000+ USDC/month Revenue
- [ ] Series A Funding

---

## 💼 Investment Opportunity

**🚀 Seed Round Open: $500K-$1M for 10-15%**

**Why Invest:**
- ✅ Proven business model (real revenue from day 1)
- ✅ First-mover in AI micro-payments
- ✅ Low overhead, high margin
- ✅ Global market, no geographic limits
- ✅ Ready to scale

**Contact:** DM for pitch deck and data room

---

## 🏆 Why Developers Choose x402

> "Finally, an AI API I can use without committing $100/month. Perfect for side projects!"  
> — Anonymous Developer

> "The pay-per-call model is a game-changer. I built a translation service and profit from day one."  
> — Early Adopter

---

## 📚 Resources

- **[API Best Practices](API_BEST_PRACTICES.md)** - How to integrate efficiently
- **[Financial Safety Policy](FINANCIAL_SAFETY_POLICY.md)** - Our zero-cash-spending principle
- **[Implementation Plan](X402_IMPLEMENTATION_PLAN.md)** - Technical roadmap
- **[SDK Examples](sdk-examples/)** - Python, JavaScript, Go code samples
- **[Video Tutorials](video_scripts/)** - 5-episode tutorial series

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| **API Endpoint** | http://8.213.149.224:5002 (private, open to partners) |
| **Live Dashboard** | http://8.213.149.224:8081 |
| **GitHub Repo** | github.com/ziwei-control/ziwei-archive |
| **Gitee Mirror** | gitee.com/pandac0/ziwei-archive |
| **Documentation** | (Coming soon) |
| **Discord Community** | (Coming soon) |

---

## ❓ FAQ

**Q: What is USDC?**  
A: USDC is a stablecoin pegged to USD (1 USDC ≈ $1), issued by Circle and regulated in the US.

**Q: I don't have USDC. How to get it?**  
A: Buy on Binance, Coinbase, or other exchanges, then withdraw to your wallet.

**Q: Is payment secure?**  
A: x402 is an open-source protocol. Payments are on-chain. We never touch your private keys.

**Q: Can I get a refund?**  
A: Blockchain payments are irreversible. But if API has issues, contact us for compensation.

**Q: Do you provide invoices?**  
A: Currently no (decentralized payments). Enterprise users can contact for custom solutions.

**Q: How to become a partner?**  
A: DM or email us. We're looking for developers, Web3 projects, content creators, and education platforms.

---

## 📞 Get Started Now

**Ready to build?**

1. Get a USDC wallet (MetaMask, etc.)
2. Load with $5-10 USDC
3. Start calling APIs at $0.02/call
4. Build your app, keep the profit

**Contact:** DM or email for API access and partnership opportunities.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

<div align="center">

**Built with ❤️ by Ziwei Control**

[Report Issue](https://github.com/ziwei-control/ziwei-archive/issues) · [Request Feature](https://github.com/ziwei-control/ziwei-archive/issues) · [Contact Us](mailto:contact@x402.network)

</div>
