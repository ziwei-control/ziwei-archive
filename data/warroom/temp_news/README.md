# 📰 时效新闻保管库

**全球战情室 - 新闻暂存管理系统**

---

## 📁 保管库位置

```
/home/admin/Ziwei/data/warroom/temp_news/
```

---

## 🎯 功能说明

### 1️⃣ 新闻暂存
- 自动从全球战情室情报中提取新闻
- 保存到时效新闻保管库
- 每小时自动更新一次

### 2️⃣ 自动清理
- **保留期限：** 2 天
- **清理频率：** 每 2 日执行一次
- **清理时间：** 凌晨 2 点
- **清理规则：** 删除 2 天前的旧闻

### 3️⃣ 新闻来源
监控 20+ 个主流币种新闻：
- BTC, ETH, BNB, XRP, SOL
- ADA, DOGE, TRX, AVAX, LINK
- USDT, USDC, STETH, WBTC 等

---

## 🔧 管理命令

### 查看状态
```bash
python3 /home/admin/Ziwei/scripts/news_temp_manager.py status
```

### 手动暂存新闻
```bash
python3 /home/admin/Ziwei/scripts/news_temp_manager.py copy
```

### 手动清理旧闻
```bash
python3 /home/admin/Ziwei/scripts/news_temp_manager.py cleanup
```

### 查看摘要
```bash
python3 /home/admin/Ziwei/scripts/news_temp_manager.py summary
```

### 获取统计数据（JSON 格式）
```bash
python3 /home/admin/Ziwei/scripts/get_temp_news_stats.py
```

---

## ⏰ 定时任务

**配置文件：** `/etc/cron.d/ziwei_news_temp`

**任务安排：**
```cron
# 清理旧闻（每 2 天的凌晨 2 点）
0 2 */2 * * root /usr/bin/python3 /home/admin/Ziwei/scripts/news_temp_manager.py cleanup

# 暂存新闻（每小时执行一次）
0 * * * * root /usr/bin/python3 /home/admin/Ziwei/scripts/news_temp_manager.py copy
```

---

## 📊 文件命名规则

**格式：** `news_YYYYMMDD_HHMMSS.json`

**示例：**
```
news_20260305_112246.json
news_20260305_143000.json
news_20260306_090000.json
```

**文件内容：**
```json
{
  "source_file": "intel_20260305_112026.json",
  "timestamp": "2026-03-05T11:20:26",
  "collected_at": "2026-03-05T11:22:46",
  "news": {
    "BTC": [...],
    "ETH": [...],
    ...
  },
  "total_items": 200
}
```

---

## 🗑️ 清理规则

### 清理逻辑
1. 计算当前时间的 2 天前作为阈值
2. 遍历所有暂存文件
3. 从文件名提取时间戳
4. 删除早于阈值的文件
5. 保留最近 2 天的文件

### 示例
```
当前时间：2026-03-05 11:00
清理阈值：2026-03-03 11:00

保留：
✅ news_20260305_100000.json (2026-03-05)
✅ news_20260304_150000.json (2026-03-04)
✅ news_20260303_120000.json (2026-03-03 12:00)

删除：
❌ news_20260303_100000.json (2026-03-03 10:00 < 阈值)
❌ news_20260302_180000.json (2026-03-02)
❌ news_20260301_090000.json (2026-03-01)
```

---

## 📈 统计数据

**查看当前统计：**
```bash
python3 /home/admin/Ziwei/scripts/get_temp_news_stats.py
```

**返回数据：**
```json
{
  "status": "success",
  "total_files": 48,           // 总文件数
  "total_news": 9600,          // 总新闻数
  "total_size_kb": 4632.5,     // 总大小
  "sources_count": 20,         // 新闻来源数量
  "sources": ["BTC", "ETH", ...],  // 来源列表
  "latest_file": "news_20260305_110000.json",
  "latest_time": "2026-03-05T11:00:00",
  "oldest_file": "news_20260303_120000.json",
  "oldest_time": "2026-03-03T12:00:00",
  "cutoff_time": "2026-03-03T11:00:00",
  "retention_days": 2
}
```

---

## 🔍 日志位置

**暂存日志：**
```
/tmp/news_temp_copy.log
```

**清理日志：**
```
/tmp/news_temp_cleanup.log
```

**查看日志：**
```bash
tail -f /tmp/news_temp_copy.log
tail -f /tmp/news_temp_cleanup.log
```

---

## 📋 使用示例

### 示例 1：查看当前状态
```bash
$ python3 /home/admin/Ziwei/scripts/news_temp_manager.py status

======================================================================
📰 时效新闻保管库管理系统
======================================================================

✅ 时效新闻保管库：/home/admin/Ziwei/data/warroom/temp_news

📊 保管库状态...
保管库位置：/home/admin/Ziwei/data/warroom/temp_news
文件数量：48
总大小：4632.50 KB
```

### 示例 2：手动暂存新闻
```bash
$ python3 /home/admin/Ziwei/scripts/news_temp_manager.py copy

======================================================================
📰 时效新闻保管库管理系统
======================================================================

✅ 时效新闻保管库：/home/admin/Ziwei/data/warroom/temp_news

📥 复制新闻到暂存库...
📄 读取最新情报：intel_20260305_112026.json
✅ 新闻已暂存：news_20260305_112246.json
   新闻总数：200 条
```

### 示例 3：清理旧闻
```bash
$ python3 /home/admin/Ziwei/scripts/news_temp_manager.py cleanup

======================================================================
📰 时效新闻保管库管理系统
======================================================================

✅ 时效新闻保管库：/home/admin/Ziwei/data/warroom/temp_news

🧹 清理 2 天前的旧闻...

🗑️  已删除：news_20260302_100000.json (2026-03-02 10:00)
🗑️  已删除：news_20260302_110000.json (2026-03-02 11:00)
🗑️  已删除：news_20260302_120000.json (2026-03-02 12:00)

📊 清理完成:
   删除旧闻：12 个文件
   保留新闻：36 个文件
   清理阈值：2026-03-03 11:00
```

### 示例 4：查看新闻摘要
```bash
$ python3 /home/admin/Ziwei/scripts/news_temp_manager.py summary

======================================================================
📰 时效新闻保管库管理系统
======================================================================

✅ 时效新闻保管库：/home/admin/Ziwei/data/warroom/temp_news

📊 暂存新闻摘要...
总文件数：36
总新闻数：7200

📄 news_20260305_110000.json
   时间：2026-03-05T11:00:00
   新闻：200 条
   来源：BTC, ETH, BNB, XRP, SOL, ADA, DOGE, TRX, AVAX, LINK

📄 news_20260305_100000.json
   时间：2026-03-05T10:00:00
   新闻：200 条
   来源：BTC, ETH, BNB, XRP, SOL, ADA, DOGE, TRX, AVAX, LINK

... (显示最近 10 个文件)
```

---

## 🌐 Dashboard 集成

**全球战情室面板显示：**
- 📰 时效新闻保管库状态
- 📊 暂存文件数量
- 📈 新闻总数
- 🗑️ 清理阈值
- ⏰ 下次清理时间

**数据接口：**
```bash
python3 /home/admin/Ziwei/scripts/get_temp_news_stats.py
```

---

## ⚠️ 注意事项

1. **保留期限：** 新闻只保留 2 天，请及时查看
2. **自动清理：** 每 2 日凌晨 2 点自动执行
3. **磁盘空间：** 注意监控保管库大小，避免占用过多空间
4. **手动备份：** 如需长期保存，请手动备份重要新闻

---

## 📞 维护命令

### 查看定时任务状态
```bash
systemctl status cron
```

### 手动触发定时任务
```bash
run-parts /etc/cron.d/
```

### 检查 cron 日志
```bash
grep CRON /var/log/cron.log | tail -20
```

### 测试脚本
```bash
# 测试暂存功能
python3 /home/admin/Ziwei/scripts/news_temp_manager.py copy

# 测试清理功能
python3 /home/admin/Ziwei/scripts/news_temp_manager.py cleanup

# 测试统计功能
python3 /home/admin/Ziwei/scripts/get_temp_news_stats.py
```

---

**文档版本：** v1.0  
**创建时间：** 2026-03-05  
**维护者：** 紫微智控 AI Assistant  
**状态：** ✅ 已启用
