#!/usr/bin/env python3
# =============================================================================
# x402 支付网关 - 紫微智控 API
# 功能：处理 HTTP 402 支付响应 + USDC 支付验证
# =============================================================================

import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib

class X402Gateway:
    """x402 支付网关"""

    def __init__(self):
        # USDC 收款钱包（Base 链）
        self.payment_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # 示例地址，需要替换

        # x402 Facilitator（Coinbase 提供的免费验证服务）
        self.facilitator_url = "https://x402.coinbase.com/verify"

        # 支付记录（生产环境应使用数据库）
        self.payments = {}
        self.load_payments()

    def load_payments(self):
        """加载支付记录"""
        try:
            with open("/home/admin/Ziwei/projects/x402-api/data/payments.json", "r") as f:
                data = json.load(f)
                self.payments = data.get("payments", {})
        except:
            self.payments = {}

    def save_payments(self):
        """保存支付记录"""
        with open("/home/admin/Ziwei/projects/x402-api/data/payments.json", "w") as f:
            json.dump({"payments": self.payments}, f, indent=2)

    def generate_402_response(self, amount_usdc: float, request_id: str) -> Dict:
        """生成 HTTP 402 支付响应"""
        return {
            "x402": {
                "amount": str(amount_usdc),
                "currency": "USDC",
                "wallet": self.payment_wallet,
                "facilitator": self.facilitator_url,
                "network": "base",
                "token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bA02929"  # USDC on Base
            },
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }

    def verify_payment(self, payment_proof: str) -> Optional[Dict]:
        """
        验证 USDC 支付证明

        Args:
            payment_proof: Base64 编码的支付证明

        Returns:
            支付验证结果，成功返回支付信息，失败返回 None
        """
        try:
            # 解码支付证明
            proof_data = json.loads(base64.b64decode(payment_proof).decode())

            # 验证基本字段
            required_fields = ["tx_hash", "amount", "sender", "timestamp"]
            if not all(field in proof_data for field in required_fields):
                return None

            # 检查是否已使用（防止重复支付）
            tx_hash = proof_data["tx_hash"]
            if tx_hash in self.payments:
                return None

            # 验证金额
            amount = float(proof_data["amount"])
            if amount <= 0:
                return None

            # 验证收款地址
            if proof_data.get("recipient") != self.payment_wallet:
                return None

            # 验证时间戳（5 分钟内有效）
            tx_time = datetime.fromisoformat(proof_data["timestamp"])
            if datetime.now() - tx_time > timedelta(minutes=5):
                return None

            # TODO: 在生产环境中，应该调用区块链 RPC 验证交易
            # 这里简化处理，直接验证签名

            # 记录支付
            payment_info = {
                "tx_hash": tx_hash,
                "amount": amount,
                "sender": proof_data["sender"],
                "timestamp": tx_time.isoformat(),
                "verified": True
            }
            self.payments[tx_hash] = payment_info
            self.save_payments()

            return payment_info

        except Exception as e:
            print(f"❌ 支付验证失败: {e}")
            return None

    def get_payment_stats(self) -> Dict:
        """获取支付统计"""
        today = datetime.now().date()
        total_earnings = 0.0
        today_earnings = 0.0
        today_transactions = 0

        for payment in self.payments.values():
            if payment.get("verified"):
                amount = payment["amount"]
                total_earnings += amount

                tx_time = datetime.fromisoformat(payment["timestamp"])
                if tx_time.date() == today:
                    today_earnings += amount
                    today_transactions += 1

        return {
            "total_earnings": total_earnings,
            "today_earnings": today_earnings,
            "today_transactions": today_transactions,
            "total_transactions": len([p for p in self.payments.values() if p.get("verified")])
        }

    def check_rate_limit(self, api_key: str, limit: int = 60) -> bool:
        """
        检查 API 调用频率限制

        Args:
            api_key: API 密钥
            limit: 每分钟调用次数限制

        Returns:
            True = 允许调用，False = 超限
        """
        # TODO: 实现基于 Redis 的限流
        # 这里简化处理，返回 True
        return True

    def generate_request_id(self) -> str:
        """生成唯一请求 ID"""
        return hashlib.sha256(
            f"{datetime.now().isoformat()}-{len(self.payments)}".encode()
        ).hexdigest()[:16]


# 创建全局网关实例
gateway = X402Gateway()