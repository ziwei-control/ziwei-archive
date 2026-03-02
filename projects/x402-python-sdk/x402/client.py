"""
x402 客户端
"""

import json
import base64
import hashlib
import requests
from .payment import Payment
from .exceptions import X402Error, PaymentError, NetworkError


class X402Client:
    """x402 客户端"""

    def __init__(self, api_base_url="http://localhost:5000", wallet_address=None):
        """
        初始化客户端

        Args:
            api_base_url: API 基础 URL
            wallet_address: 钱包地址（用于支付）
        """
        self.api_base_url = api_base_url
        self.wallet_address = wallet_address
        self.session = requests.Session()

    def request_with_payment(self, endpoint, method="POST", json_data=None, **kwargs):
        """
        发起带支付请求

        Args:
            endpoint: API 端点（如 /api/v1/code-audit）
            method: HTTP 方法
            json_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应 JSON 数据
        """
        url = f"{self.api_base_url}{endpoint}"

        # 第一次请求（无支付）
        response = self.session.request(method, url, json=json_data, **kwargs)

        # 检查是否需要支付
        if response.status_code == 402:
            x402_info = response.json().get('x402')

            if not x402_info:
                raise X402Error("无效的 402 响应")

            print(f"💰 需要支付: {x402_info['amount']} {x402_info['currency']}")
            print(f"📍 钱包地址: {x402_info['wallet']}")

            # TODO: 完成实际支付（这里模拟）
            # 实际应用中需要集成钱包并完成 USDC 转账
            payment_proof = self._mock_payment(x402_info)

            # 重发请求 + 支付证明
            headers = kwargs.get('headers', {})
            headers['x-payment-proof'] = payment_proof
            kwargs['headers'] = headers

            response = self.session.request(method, url, json=json_data, **kwargs)

        # 检查最终响应
        if response.status_code == 200:
            return response.json()
        else:
            raise X402Error(f"请求失败: {response.status_code} - {response.text}")

    def _mock_payment(self, x402_info):
        """
        模拟支付（用于测试）

        Args:
            x402_info: x402 支付信息

        Returns:
            支付证明
        """
        # 模拟交易哈希
        mock_tx_hash = "0x" + "0" * 64

        # 创建支付证明
        return Payment.create_payment_proof(
            tx_hash=mock_tx_hash,
            amount=x402_info['amount'],
            sender=self.wallet_address or "0x" + "1" * 40,
            recipient=x402_info['wallet']
        )

    def get_stats(self):
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        url = f"{self.api_base_url}/api/v1/stats"
        response = self.session.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise NetworkError(f"获取统计失败: {response.status_code}")

    def health_check(self):
        """
        健康检查

        Returns:
            健康状态
        """
        url = f"{self.api_base_url}/health"
        response = self.session.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise NetworkError(f"健康检查失败: {response.status_code}")