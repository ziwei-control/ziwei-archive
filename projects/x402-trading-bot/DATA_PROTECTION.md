# 🔒 交易数据保护机制

**版本：** v1.0  
**生效时间：** 2026-03-10  
**目的：** 杜绝因系统重启、断电、Bug 导致的交易数据丢失

---

## ⚠️ 历史教训

**2026-03-10 SOL 丢失事件：**
- 3 月 9 日 16:50 建仓 SOL 5.6411 @ $83.51 = $471.09
- 3 月 10 日 13:44 策略引擎重启
- **结果：** SOL 持仓记录丢失，策略重新建仓时没有选择 SOL
- **损失：** 不是交易亏损，是系统问题白亏 $471

**根本原因：**
1. 旧代码没有独立保存交易历史
2. 重启时只读取 account_status.json，但里面没有 SOL 记录
3. 没有外部记录可以恢复

---

## 🛡️ 新的保护机制

### 1. 交易历史独立持久化 ⭐⭐⭐⭐⭐

**文件：** `/home/admin/Ziwei/data/strategy/trade_history.jsonl`

**格式：** JSON Lines（每行一笔交易，追加模式）

```json
{"type": "建仓", "symbol": "DOGE", "time": "2026-03-10T14:15:38.757291", "price": 0.091707, "amount": 6106.40, "value": 560.0, "pnl": 0}
{"type": "加仓", "symbol": "DOGE", "time": "2026-03-10T14:16:38.123456", "price": 0.091858, "amount": 7140.11, "value": 655.88, "pnl": 0}
{"type": "清仓", "symbol": "BTC", "time": "2026-03-10T15:30:00.000000", "price": 70000, "amount": 0.01, "value": 700.0, "pnl": 50.0}
```

**特点：**
- ✅ 每笔交易**立即**写入文件
- ✅ **追加模式**，永不覆盖
- ✅ 即使程序崩溃也不丢失
- ✅ 可以恢复任意时间点的状态

---

### 2. 自动备份机制 ⭐⭐⭐⭐⭐

**目录：** `/home/admin/Ziwei/data/strategy/backup/`

**备份策略：**
- 每次交易后自动备份
- 保留最近 100 个备份
- 最新备份：`account_status_latest.json`
- 时间戳备份：`account_status_20260310_141538.json`

**恢复命令：**
```bash
# 恢复到最新备份
cp /home/admin/Ziwei/data/strategy/backup/account_status_latest.json \
   /home/admin/Ziwei/data/strategy/account_status.json

# 恢复到指定时间点
cp /home/admin/Ziwei/data/strategy/backup/account_status_20260310_141538.json \
   /home/admin/Ziwei/data/strategy/account_status.json
```

---

### 3. 启动时自动对账 ⭐⭐⭐⭐⭐

**流程：**
```
1. 从 trade_history.jsonl 加载（最可靠）
2. 从 account_status.json 补充
3. 从最新备份补充
4. 从日志文件恢复未记录的交易
5. 合并去重，恢复完整历史
```

**日志输出：**
```
✅ 从独立文件加载交易历史：75 笔
✅ 从账户状态补充加载：75 笔
✅ 从日志恢复交易：0 笔
📜 总交易历史：75 笔
```

---

### 4. 恢复工具 ⭐⭐⭐⭐

**脚本：** `/home/admin/Ziwei/projects/x402-trading-bot/recover_history.py`

**用途：** 手动恢复交易历史

**使用方法：**
```bash
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 recover_history.py
```

**输出：**
```
======================================================================
📜 交易历史恢复工具
======================================================================
✅ 从 trade_history.jsonl 加载：75 笔
✅ 从 account_status.json 加载：75 笔
✅ 从最新备份加载：75 笔
✅ 从日志恢复：10 笔

📊 统计结果:
  原始总数：230 笔
  去重后：75 笔

📦 按币种统计:
  DOGE: 20 笔
  BTC: 18 笔
  XRP: 12 笔
  BNB: 10 笔
  ADA: 15 笔

📜 最近 10 笔交易:
  加仓 DOGE @ 2026-03-10T14:20:15
  加仓 BTC @ 2026-03-10T14:20:15
  ...

💾 恢复结果已保存：/home/admin/Ziwei/data/strategy/recovered_history.json
======================================================================
```

---

## 📊 数据流向

```
交易发生
    ↓
内存中的 trade_history 数组
    ↓
立即写入 trade_history.jsonl (独立文件)
    ↓
同时更新 account_status.json
    ↓
自动创建备份到 backup/
    ↓
下次启动时自动对账恢复
```

---

## 🔧 验证方法

### 检查交易历史是否持久化

```bash
# 查看最新交易记录
tail -10 /home/admin/Ziwei/data/strategy/trade_history.jsonl

# 统计交易总数
wc -l /home/admin/Ziwei/data/strategy/trade_history.jsonl

# 查看备份
ls -la /home/admin/Ziwei/data/strategy/backup/
```

### 模拟重启测试

```bash
# 1. 查看当前交易数
tail -1 /home/admin/Ziwei/data/strategy/trade_history.jsonl

# 2. 重启策略引擎
pkill -f strategy_engine_v3.py
sleep 2
cd /home/admin/Ziwei/projects/x402-trading-bot
nohup python3 strategy_engine_v3.py > /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log 2>&1 &

# 3. 查看日志，确认交易历史已恢复
tail -30 /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log | grep "已加载交易历史"
```

**预期输出：**
```
✅ 从独立文件加载交易历史：75 笔
📜 总交易历史：75 笔
```

---

## 🚨 故障恢复流程

### 场景 1：策略引擎重启后交易历史丢失

```bash
# 1. 停止策略引擎
pkill -f strategy_engine_v3.py

# 2. 运行恢复工具
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 recover_history.py

# 3. 检查恢复结果
cat /home/admin/Ziwei/data/strategy/recovered_history.json | python3 -m json.tool | head -50

# 4. 重启策略引擎
nohup python3 strategy_engine_v3.py > /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log 2>&1 &
```

### 场景 2：trade_history.jsonl 损坏

```bash
# 1. 从备份恢复
cp /home/admin/Ziwei/data/strategy/backup/account_status_latest.json \
   /home/admin/Ziwei/data/strategy/account_status.json

# 2. 从账户状态重建 jsonl
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 -c "
import json
from pathlib import Path

account_file = Path('/home/admin/Ziwei/data/strategy/account_status.json')
jsonl_file = Path('/home/admin/Ziwei/data/strategy/trade_history.jsonl')

with open(account_file) as f:
    account = json.load(f)

history = account.get('trade_history', [])

with open(jsonl_file, 'w', encoding='utf-8') as f:
    for trade in history:
        f.write(json.dumps(trade, ensure_ascii=False) + '\n')

print(f'✅ 已重建交易历史：{len(history)} 笔')
"

# 3. 重启策略引擎
```

### 场景 3：服务器断电后恢复

```bash
# 1. 检查文件系统
fsck /dev/sda1  # 如果需要

# 2. 检查数据完整性
ls -la /home/admin/Ziwei/data/strategy/
ls -la /home/admin/Ziwei/data/strategy/backup/

# 3. 运行恢复工具
cd /home/admin/Ziwei/projects/x402-trading-bot
python3 recover_history.py

# 4. 验证恢复结果
cat /home/admin/Ziwei/data/strategy/recovered_history.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'恢复交易：{len(d)} 笔')
"

# 5. 重启策略引擎
```

---

## 📈 监控建议

### 每日检查

```bash
# 检查交易历史文件大小
ls -lh /home/admin/Ziwei/data/strategy/trade_history.jsonl

# 检查备份数量
ls /home/admin/Ziwei/data/strategy/backup/ | wc -l

# 检查最新交易时间
tail -1 /home/admin/Ziwei/data/strategy/trade_history.jsonl | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'最后交易：{d.get(\"time\", \"N/A\")}')
"
```

### 每周检查

```bash
# 对比内存和持久化的交易数
tail -30 /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log | grep "交易历史"

# 检查是否有异常
grep -E "❌|失败|Error" /home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log
```

---

## ✅ 验证清单

每次策略引擎重启后检查：

- [ ] 交易历史数量正确（查看日志输出）
- [ ] 当前持仓与重启前一致
- [ ] trade_history.jsonl 文件存在且有内容
- [ ] 最新备份已创建
- [ ] Dashboard 显示的交易时间线正确

---

## 📞 紧急联系

如果数据恢复失败：

1. 检查日志文件：`/home/admin/Ziwei/data/logs/soul-trader/strategy_engine_v3.log`
2. 检查备份文件：`/home/admin/Ziwei/data/strategy/backup/`
3. 运行恢复工具：`python3 recover_history.py`
4. 查看恢复报告：`/home/admin/Ziwei/data/strategy/recovered_history.json`

---

**最后更新：** 2026-03-10  
**责任人：** AI Assistant  
**状态：** ✅ 已实施
