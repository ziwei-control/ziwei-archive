"""
x402 异常定义
"""


class X402Error(Exception):
    """x402 基础异常"""
    pass


class PaymentError(X402Error):
    """支付错误"""
    pass


class NetworkError(X402Error):
    """网络错误"""
    pass


class WalletError(X402Error):
    """钱包错误"""
    pass