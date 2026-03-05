#!/usr/bin/env python3
"""
x402 API 密钥自动生成系统

功能：
1. 监控 USDC 收款地址的交易
2. 验证交易金额（0.05 USDC ±0.02）
3. 自动生成 API_KEY
4. 返回真实的 API_BASE_URL

使用方式：
python3 api_key_generator.py --tx-hash <交易哈希>
或
python3 api_key_generator.py --auto-monitor  # 自动监控模式
"""

import hashlib
import json
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

# ============ 配置 ============
PAYMENT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
EXPECTED_AMOUNT = 0.05  # USDC
TOLERANCE = 0.02  # 容差范围
REAL_API_URL = "8.213.149.224"
BASESCAN_API_KEY = ""  # TODO: 替换为你的 BaseScan API Key（免费申请：https://basescan.org/myapikey）

# ============ BaseScan API 封装 ============
class BaseScanAPI:
    """BaseScan API 封装"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.basescan.org/api"
    
    def get_token_transfers(self, address: str) -> Optional[Dict[str, Any]]:
        """获取地址的 USDC 转账记录"""
        import requests
        
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": self.api_key if self.api_key else "YourBaseScanApiKey"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 查询失败：{e}")
            return None
    
    def verify_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """验证特定交易"""
        import requests
        
        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash,
            "apikey": self.api_key if self.api_key else "YourBaseScanApiKey"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 验证失败：{e}")
            return None

# ============ API Key 生成器 ============
class APIKeyGenerator:
    """API Key 生成器"""
    
    @staticmethod
    def generate(tx_hash: str, timestamp: int) -> str:
        """
        生成 API Key
        
        Args:
            tx_hash: 交易哈希
            timestamp: 时间戳
        
        Returns:
            生成的 API Key
        """
        # 使用固定算法生成唯一的 API Key
        salt = "x402_secret_salt_2026"
        data = f"{tx_hash}{timestamp}{salt}"
        
        # SHA256 哈希
        hash_obj = hashlib.sha256(data.encode())
        hash_hex = hash_obj.hexdigest()[:16]
        
        # 生成格式化的 API Key
        api_key = f"x402_{hash_hex}_{timestamp:x}"
        
        return api_key

# ============ 交易验证器 ============
class TransactionVerifier:
    """交易验证器"""
    
    def __init__(self, basescan_api: BaseScanAPI):
        self.api = basescan_api
    
    def verify_payment(self, tx_hash: str) -> Dict[str, Any]:
        """
        验证支付交易
        
        Args:
            tx_hash: 交易哈希
        
        Returns:
            验证结果
        """
        print(f"🔍 正在验证交易：{tx_hash}")
        
        # 查询交易详情
        tx_data = self.api.verify_transaction(tx_hash)
        
        if not tx_data or tx_data.get("status") != "1":
            return {
                "success": False,
                "message": "交易不存在或查询失败"
            }
        
        # 检查交易是否成功
        result = tx_data.get("result", {})
        if result.get("status") != "0x1":
            return {
                "success": False,
                "message": "交易失败"
            }
        
        # 检查收款地址
        to_address = result.get("to", "").lower()
        if to_address != PAYMENT_ADDRESS.lower():
            return {
                "success": False,
                "message": f"收款地址不匹配：{to_address}"
            }
        
        # 检查金额（需要查询 USDC 转账详情）
        # 这里简化处理，实际应该查询 USDC 合约的 Transfer 事件
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "timestamp": int(result.get("blockTimestamp", time.time()), 16)
        }
    
    def find_recent_payment(self, from_address: str = "") -> Dict[str, Any]:
        """
        查找最近的合格支付
        
        Args:
            from_address: 可选的发送方地址
        
        Returns:
            找到的支付信息
        """
        print(f"🔍 正在查询地址 {PAYMENT_ADDRESS} 的交易记录...")
        
        # 获取转账记录
        transfers = self.api.get_token_transfers(PAYMENT_ADDRESS)
        
        if not transfers or transfers.get("status") != "1":
            return {
                "success": False,
                "message": "未找到交易记录"
            }
        
        results = transfers.get("result", [])
        if not results:
            return {
                "success": False,
                "message": "暂无交易记录"
            }
        
        # 查找最近的合格交易
        now = time.time()
        time_window = 300  # 5 分钟
        
        for tx in results:
            # 检查是否是 USDC
            token_symbol = tx.get("tokenSymbol", "")
            token_name = tx.get("tokenName", "")
            
            if token_symbol not in ["USDC", "USD Coin"] and "USD Coin" not in token_name:
                continue
            
            # 检查金额
            try:
                decimal = int(tx.get("tokenDecimal", 6))
                value = int(tx.get("value", 0))
                amount = value / (10 ** decimal)
                
                # 检查金额是否在容差范围内
                if abs(amount - EXPECTED_AMOUNT) > TOLERANCE:
                    continue
                
                # 检查时间
                tx_time = int(tx.get("timeStamp", 0))
                if (now - tx_time) > time_window:
                    continue
                
                # 如果指定了发送方地址，检查是否匹配
                if from_address and tx.get("from", "").lower() != from_address.lower():
                    continue
                
                # 找到合格交易
                print(f"✅ 找到合格交易：{tx.get('hash')}")
                print(f"   金额：{amount} USDC")
                print(f"   时间：{datetime.fromtimestamp(tx_time)}")
                
                return {
                    "success": True,
                    "tx_hash": tx.get("hash"),
                    "amount": amount,
                    "timestamp": tx_time,
                    "from": tx.get("from")
                }
                
            except Exception as e:
                print(f"⚠️ 解析交易失败：{e}")
                continue
        
        return {
            "success": False,
            "message": "未找到符合条件的交易"
        }

# ============ 主程序 ============
def main():
    parser = argparse.ArgumentParser(description="x402 API 密钥生成器")
    parser.add_argument("--tx-hash", type=str, help="交易哈希")
    parser.add_argument("--from-address", type=str, help="发送方地址（可选）")
    parser.add_argument("--auto-monitor", action="store_true", help="自动监控模式")
    parser.add_argument("--api-key", type=str, default=BASESCAN_API_KEY, help="BaseScan API Key")
    
    args = parser.parse_args()
    
    # 初始化
    basescan = BaseScanAPI(args.api_key)
    verifier = TransactionVerifier(basescan)
    generator = APIKeyGenerator()
    
    print("=" * 60)
    print("x402 API 密钥自动生成系统")
    print("=" * 60)
    print(f"收款地址：{PAYMENT_ADDRESS}")
    print(f"期望金额：{EXPECTED_AMOUNT} USDC (容差：±{TOLERANCE})")
    print(f"真实 API 地址：{REAL_API_URL}")
    print("=" * 60)
    
    if args.auto_monitor:
        # 自动监控模式
        print("\n🔍 启动自动监控模式... (Ctrl+C 停止)")
        last_tx = ""
        
        try:
            while True:
                result = verifier.find_recent_payment()
                
                if result["success"] and result["tx_hash"] != last_tx:
                    last_tx = result["tx_hash"]
                    
                    # 生成 API Key
                    api_key = generator.generate(result["tx_hash"], result["timestamp"])
                    
                    print("\n" + "=" * 60)
                    print("✅ 验证成功！")
                    print("=" * 60)
                    print(f"API_BASE_URL: {REAL_API_URL}")
                    print(f"API_KEY: {api_key}")
                    print(f"交易哈希：{result['tx_hash']}")
                    print(f"支付金额：{result['amount']} USDC")
                    print("=" * 60)
                
                time.sleep(10)  # 每 10 秒检查一次
                
        except KeyboardInterrupt:
            print("\n\n停止监控")
    
    elif args.tx_hash:
        # 验证特定交易
        result = verifier.verify_payment(args.tx_hash)
        
        if result["success"]:
            # 生成 API Key
            api_key = generator.generate(result["tx_hash"], result["timestamp"])
            
            print("\n" + "=" * 60)
            print("✅ 验证成功！")
            print("=" * 60)
            print(f"API_BASE_URL: {REAL_API_URL}")
            print(f"API_KEY: {api_key}")
            print(f"交易哈希：{result['tx_hash']}")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 验证失败")
            print("=" * 60)
            print(f"原因：{result['message']}")
            print(f"请发送 {EXPECTED_AMOUNT} USDC 到：{PAYMENT_ADDRESS}")
            print("=" * 60)
    
    else:
        # 查找最近的合格支付
        from_addr = args.from_address if args.from_address else ""
        result = verifier.find_recent_payment(from_addr)
        
        if result["success"]:
            # 生成 API Key
            api_key = generator.generate(result["tx_hash"], result["timestamp"])
            
            print("\n" + "=" * 60)
            print("✅ 验证成功！")
            print("=" * 60)
            print(f"API_BASE_URL: {REAL_API_URL}")
            print(f"API_KEY: {api_key}")
            print(f"交易哈希：{result['tx_hash']}")
            print(f"支付金额：{result['amount']} USDC")
            print(f"发送方：{result.get('from', 'Unknown')}")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 未查询到交易")
            print("=" * 60)
            print(f"原因：{result['message']}")
            print(f"\n请发送 {EXPECTED_AMOUNT} USDC 到：")
            print(f"{PAYMENT_ADDRESS}")
            print(f"\n容差范围：{EXPECTED_AMOUNT - TOLERANCE} - {EXPECTED_AMOUNT + TOLERANCE} USDC")
            print("=" * 60)

if __name__ == "__main__":
    main()
