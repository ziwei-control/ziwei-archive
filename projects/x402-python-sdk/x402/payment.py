"""
x402 支付处理
"""

import json
import base64
from datetime import datetime
from .exceptions import PaymentError


class Payment:
    """x402 支付处理类"""

    @staticmethod
    def create_payment_proof(tx_hash, amount, sender, recipient):
        """
        创建支付证明

        Args:
            tx_hash: 交易哈希
            amount: 支付金额
            sender: 发送方地址
            recipient: 接收方地址

        Returns:
            Base64 编码的支付证明
        """
        proof = {
            "tx_hash": tx_hash,
            "amount": str(amount),
            "sender": sender,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat()
        }
        return base64.b64encode(json.dumps(proof).encode()).decode()

    @staticmethod
    def decode_payment_proof(proof_base64):
        """
        解码支付证明

        Args:
            proof_base64: Base64 编码的支付证明

        Returns:
            支付证明字典
        """
        try:
            return json.loads(base64.b64decode(proof_base64).decode())
        except Exception as e:
            raise PaymentError(f"无效的支付证明: {e}")

    @staticmethod
    def validate_payment_proof(proof):
        """
        验证支付证明

        Args:
            proof: 支付证明字典

        Returns:
            验证结果
        """
        required_fields = ["tx_hash", "amount", "sender", "recipient", "timestamp"]
        for field in required_fields:
            if field not in proof:
                raise PaymentError(f"缺少必要字段: {field}")

        if not proof["tx_hash"].startswith("0x"):
            raise PaymentError("无效的交易哈希")

        try:
            float(proof["amount"])
        except:
            raise PaymentError("无效的金额")

        return True