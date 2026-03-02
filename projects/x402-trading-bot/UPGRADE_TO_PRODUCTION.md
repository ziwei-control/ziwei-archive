# x402 交易机器人 - 正式版升级方案

## 🎯 目标

将模拟版升级为**真实交易版**，支持真实的交易所API连接和资金操作。

---

## ⚠️ 重要警告

**🔴 高风险！仅使用能承受损失的资金！**

**风险提示**：
- 可能导致部分或全部资金损失
- 市场波动不可预测
- 策略可能失效
- 交易所API可能有延迟或故障

**最大亏损风险**: 投入资金的 20-50%

---

## 📋 升级步骤

### 第 1 步：选择交易所

推荐选项：

| 交易所 | 优势 | 适用场景 |
|--------|------|---------|
| **Binance** | 流动性最好，API稳定 | 主力交易 |
| **OKX** | 手续费低，API友好 | 低频交易 |
| **Bybit** | 衍生品丰富，API快 | 杠杆交易 |
| **Phemex** | 支持 x402 生态代币 | 生态代币交易 |

### 第 2 步：创建 API 密钥

在选择的交易所设置中：

1. 进入 API 管理页面
2. 创建新 API 密钥
3. **重要**：设置 IP 白名单（服务器 IP）
4. **重要**：不开启提币权限（除非需要）
5. 复制 API Key 和 Secret

### 第 3 步：配置机器人

创建配置文件：

```python
# config.py
EXCHANGE_CONFIG = {
    # 交易所选择
    "exchange": "binance",  # 或 okx, bybit, phemex
    
    # API 密钥（从交易所获取）
    "api_key": "your-api-key-here",
    "api_secret": "your-api-secret-here",
    
    # 交易对
    "trading_pairs": {
        "VIRTUAL/USDT": {
            "symbol": "VIRTUALUSDT",
            "test_order": True  # 测试订单模式
        },
        "PAYAI/USDT": {
            "symbol": "PAYAIUSDT",
            "test_order": True
        },
        "PING/USDT": {
            "symbol": "PINGUSDT",
            "test_order": True
        }
    },
    
    # 风险控制
    "max_position_size": 0.2,  # 最大仓位 20%
    "stop_loss": -0.10,          # 止损 -10%
    "take_profit": 0.05,         # 止盈 +5%
    "max_drawdown": -0.15,       # 最大回撤 -15%
    
    # 测试模式
    "test_mode": True,          # 启用测试模式
    "dry_run": True             # 模拟下单（不真实交易）
}
```

### 第 4 步：升级代码

需要实现的功能：

```python
# 1. 交易所API连接
import ccxt

class RealExchangeConnector:
    def __init__(self, exchange, api_key, api_secret):
        self.exchange = getattr(ccxt, exchange)()
        self.exchange.api_key = api_key
        self.exchange.secret = api_secret
        self.exchange.enable_rateLimit = True
    
    def get_balance(self):
        """获取账户余额"""
        return self.exchange.fetch_balance()
    
    def get_ticker(self, symbol):
        """获取当前价格"""
        return self.exchange.fetch_ticker(symbol)
    
    def place_order(self, symbol, side, amount, price=None):
        """下订单"""
        if self.exchange.options.get('createMarketOrder'):
            return self.exchange.create_market_order(symbol, side, amount)
        else:
            return self.exchange.create_limit_order(symbol, side, amount, price)
    
    def cancel_order(self, order_id):
        """取消订单"""
        return self.exchange.cancel_order(order_id)
    
    def get_order(self, order_id):
        """查询订单"""
        return self.fetch_order(order_id)
    
    def get_open_orders(self, symbol):
        """获取挂单"""
        return self.exchange.fetch_open_orders(symbol)
    
    def get_my_trades(self, symbol):
        """获取历史交易"""
        return self.exchange.fetch_my_trades(symbol)

# 2. 真实钱包连接
import json
from web3 import Web3

class WalletConnector:
    def __init__(self, private_key, network="mainnet"):
        self.private_key = private_key
        self.network = network
        if network == "mainnet":
            self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR-PROJECT-ID"))
        else:
            self.w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/YOUR-PROJECT-ID"))
    
    def get_balance(self, token_address):
        """获取代币余额"""
        # ERC-20 代币余额查询
        pass
    
    def transfer(self, to_address, amount, token_address):
        """转账"""
        # 构建交易并发送
        pass

# 3. 风险控制系统
class RiskController:
    def __init__(self, config):
        self.max_position_size = config.get("max_position_size", 0.2)
        self.stop_loss = config.get("stop_loss", -0.10)
        self.take_profit = config.get("take_profit", 0.05)
        self.max_drawdown = config.get("max_drawdown", -0.15)
    
    def check_position_size(self, available_balance, position_value):
        """检查仓位大小"""
        max_allowed = available_balance * self.max_position_size
        if position_value > max_allowed:
            return False, f"仓位过大，最大允许 {max_allowed}"
        return True, "仓位正常"
    
    def check_stop_loss(self, current_price, entry_price):
        """检查止损"""
        pnl = (current_price - entry_price) / entry_price
        if pnl <= self.stop_loss:
            return True, f"触发止损: {pnl:.2%}"
        return False, ""
    
    def check_take_profit(self, current_price, entry_price):
        """检查止盈"""
        pnl = (current_price - entry_price) / entry_price
        if pnl >= self.take_profit:
            return True, f"触发止盈: {pnl:.2%}"
        return False, ""

# 4. 交易策略引擎
class TradingStrategy:
    def __init__(self, config):
        self.config = config
        self.risk_controller = RiskController(config)
    
    def execute_trade(self, signal, connector, wallet):
        """执行交易"""
        symbol = signal['symbol']
        side = signal['side']  # 'buy' or 'sell'
        amount = signal['amount']
        
        # 1. 获取余额
        balance = connector.get_balance()
        available = balance.get('USDT', {}).get('free', 0)
        
        # 2. 获取价格
        ticker = connector.get_ticker(symbol)
        current_price = ticker['last']
        
        # 3. 计算仓位价值
        position_value = amount * current_price
        
        # 4. 风险检查
        can_trade, reason = self.risk_controller.check_position_size(available, position_value)
        if not can_trade:
            print(f"❌ 风险检查失败: {reason}")
            return False
        
        # 5. 下单
        try:
            if self.config.get('test_mode', True):
                print(f"🧪 测试模式: {side} {amount} {symbol} @ ${current_price}")
                return True
            else:
                order = connector.place_order(symbol, side, amount, current_price)
                print(f"✅ 订单已提交: {order['id']}")
                return True
        except Exception as e:
            print(f"❌ 下单失败: {e}")
            return False

# 5. 监控和报告系统
class Monitor:
    def __init__(self):
        self.positions = {}
        self.trades = []
        self.pnl_history = []
    
    def update_position(self, symbol, entry_price, amount, side):
        """更新持仓"""
        self.positions[symbol] = {
            'entry_price': entry_price,
            'amount': amount,
            'side': side,
            'entry_time': datetime.now()
        }
    
    def check_risk(self, connector):
        """检查风险"""
        for symbol, position in self.positions.items():
            ticker = connector.get_ticker(symbol)
            current_price = ticker['last']
            
            # 检查止损
            should_sl, sl_reason = self.risk_controller.check_stop_loss(current_price, position['entry_price'])
            if should_sl:
                print(f"⚠️  {symbol}: {sl_reason}")
                # 触发止损平仓
            
            # 检查止盈
            should_tp, tp_reason = self.risk_controller.check_take_profit(current_price, position['entry_price'])
            if should_tp:
                print(f"🎯  {symbol}: {tp_reason}")
                # 触发止盈平仓
```

### 第 5 步：部署和测试

```bash
# 1. 安装依赖
pip3 install ccxt web3 python-dotenv

# 2. 配置环境变量
cat > .env << 'EOF'
EXCHANGE=binance
API_KEY=your-api-key
API_SECRET=your-api-secret
WALLET_PRIVATE_KEY=your-private-key
TEST_MODE=true
DRY_RUN=true
EOF

# 3. 启动机器人
python3 trading_bot.py
```

---

## 📁 文件结构

```
/home/admin/Ziwei/projects/x402-trading-bot/
├── bot_simple.py              # 模拟版（已存在）
├── bot_production.py          # 正式版（新建）
├── config.py                   # 配置文件
├── exchange/
│   ├── __init__.py
│   ├── base.py                 # 交易所基类
│   ├── binance.py              # Binance 连接
│   ├── okx.py                  # OKX 连接
│   ├── bybit.py                # Bybit 连接
│   └── phemex.py              # Phemex 连接
├── strategies/
│   ├── __init__.py
│   ├── grid_trading.py         # 网格交易
│   ├── trend_following.py      # 趋势跟踪
│   ├── arbitrage.py            # 套利交易
│   └── market_making.py        # 做市策略
├── risk/
│   ├── __init__.py
│   └── controller.py           # 风险控制
├── monitor/
│   ├── __init__.py
│   └── monitor.py              # 监控系统
└── data/
    ├── trades.json              # 交易记录
    └── positions.json           # 持仓记录
```

---

## 🔐 安全建议

1. **IP 白名单**: 只允许服务器 IP 访问 API
2. **权限限制**: 不开启提币权限
3. **小额开始**: 从 $10-50 开始测试
4. **止损机制**: 严格执行止损
5. **监控日志**: 24小时监控
6. **定期备份**: 备份配置和交易记录

---

## ⚖️ 免责声明

**使用本机器人进行交易，您需要完全了解并接受以下风险：**

1. 您可能会损失部分或全部投资资金
2. 市场波动可能导致重大损失
3. 技术故障可能导致交易失败
4. 策略可能在不同市场条件下失效
5. 交易所可能发生故障或被攻击

**本软件按"原样"提供，不对任何交易结果负责。**

---

## 🎯 升级路线图

### 阶段 1：连接测试网（1-2 周）
- [ ] 连接测试网 API
- [ ] 测试订单流程
- [ ] 验证风险控制
- [ ] 小额真实资金测试（$10-50）

### 阶段 2：真实交易（1-2 个月）
- [ ] 连接真实交易所
- [ ] 小额实盘交易
- [ ] 监控和优化
- [ ] 评估策略效果

### 阶段 3：规模化（3-6 个月）
- [ ] 增加资金
- [ ] 多策略并行
-  [ ] 自动化部署
-  [ ] 持续优化

---

## 📊 预期性能

| 策略 | 月收益率 | 风险等级 |
|------|----------|---------|
| 网格交易 | 1-3% | 中 |
| 趋势跟踪 | 5-10% | 中高 |
| 套利交易 | 1-5% | 低中 |
| 做市策略 | 0.5-2% | 低 |

**注意**: 实际收益可能差异很大

---

**⚠️ 重要：正式版涉及真实资金交易，请谨慎评估风险后再决定升级！**

**准备升级？请确认后告诉我。**