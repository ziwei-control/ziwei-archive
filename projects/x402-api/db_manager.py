#!/usr/bin/env python3
"""
x402 API 密钥数据库管理工具

功能：
1. 查看已发放的 API Key
2. 查看统计数据
3. 导出记录
4. 禁用/启用 API Key

使用方式：
python3 db_manager.py --list          # 列出所有
python3 db_manager.py --stats         # 查看统计
python3 db_manager.py --export        # 导出 CSV
python3 db_manager.py --disable <key> # 禁用某个 Key
"""

import sqlite3
import argparse
import csv
import sys
from datetime import datetime

DB_PATH = "api_keys.db"

def get_connection():
    """获取数据库连接"""
    if not sqlite3.connect(DB_PATH):
        print(f"❌ 数据库不存在：{DB_PATH}")
        print("请先启动 api_key_server.py 初始化数据库")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def list_keys(limit=20):
    """列出最近的 API Key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, api_key, api_base_url, tx_hash, amount, from_address, timestamp, created_at, is_active
        FROM api_keys
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("📭 暂无记录")
        return
    
    print("=" * 100)
    print(f"{'ID':<5} {'API Key':<40} {'Amount':<10} {'From':<20} {'Time':<20} {'Status':<8}")
    print("=" * 100)
    
    for row in rows:
        status = "✅ Active" if row[8] == 1 else "❌ Disabled"
        from_addr = row[5][:18] + "..." if row[5] else "Unknown"
        time_str = datetime.fromtimestamp(row[6]).strftime("%Y-%m-%d %H:%M")
        
        print(f"{row[0]:<5} {row[1]:<40} {row[4]:<10.4f} {from_addr:<20} {time_str:<20} {status:<8}")
    
    print("=" * 100)
    print(f"共 {len(rows)} 条记录")

def show_stats():
    """显示统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 总数量
    cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
    total = cursor.fetchone()[0]
    
    # 今日数量
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) FROM api_keys 
        WHERE is_active = 1 AND DATE(created_at) = ?
    """, (today,))
    today = cursor.fetchone()[0]
    
    # 总收入
    cursor.execute("SELECT SUM(amount) FROM api_keys WHERE is_active = 1")
    revenue = cursor.fetchone()[0] or 0
    
    # 平均金额
    cursor.execute("SELECT AVG(amount) FROM api_keys WHERE is_active = 1")
    avg = cursor.fetchone()[0] or 0
    
    # 最大金额
    cursor.execute("SELECT MAX(amount) FROM api_keys WHERE is_active = 1")
    max_amount = cursor.fetchone()[0] or 0
    
    # 禁用数量
    cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 0")
    disabled = cursor.fetchone()[0]
    
    conn.close()
    
    print("=" * 60)
    print("📊 x402 API Key 统计数据")
    print("=" * 60)
    print(f"总发放数量：    {total}")
    print(f"今日发放：      {today}")
    print(f"禁用数量：      {disabled}")
    print(f"总收入：        {revenue:.4f} USDC")
    print(f"平均金额：      {avg:.4f} USDC")
    print(f"最大单笔：      {max_amount:.4f} USDC")
    print("=" * 60)

def export_csv(filename="api_keys_export.csv"):
    """导出为 CSV"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT api_key, api_base_url, tx_hash, amount, from_address, timestamp, created_at, is_active
        FROM api_keys
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['API Key', 'API Base URL', 'Transaction Hash', 'Amount (USDC)', 
                        'From Address', 'Timestamp', 'Created At', 'Is Active'])
        writer.writerows(rows)
    
    print(f"✅ 已导出 {len(rows)} 条记录到 {filename}")

def disable_key(api_key):
    """禁用 API Key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE api_keys 
        SET is_active = 0 
        WHERE api_key = ?
    """, (api_key,))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ 已禁用 API Key: {api_key}")
    else:
        print(f"❌ 未找到 API Key: {api_key}")
    
    conn.close()

def enable_key(api_key):
    """启用 API Key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE api_keys 
        SET is_active = 1 
        WHERE api_key = ?
    """, (api_key,))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ 已启用 API Key: {api_key}")
    else:
        print(f"❌ 未找到 API Key: {api_key}")
    
    conn.close()

def search_key(query):
    """搜索 API Key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, api_key, api_base_url, tx_hash, amount, from_address, timestamp, created_at, is_active
        FROM api_keys
        WHERE api_key LIKE ? OR tx_hash LIKE ? OR from_address LIKE ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"🔍 未找到匹配 '{query}' 的记录")
        return
    
    print("=" * 100)
    print(f"搜索结果：{len(rows)} 条")
    print("=" * 100)
    
    for row in rows:
        status = "✅ Active" if row[8] == 1 else "❌ Disabled"
        print(f"ID: {row[0]} | Key: {row[1]} | Amount: {row[4]:.4f} USDC | Status: {status}")
        print(f"  TX: {row[3]} | From: {row[5]} | Time: {datetime.fromtimestamp(row[6])}")
        print("-" * 100)

def main():
    parser = argparse.ArgumentParser(description="x402 API Key 数据库管理工具")
    parser.add_argument("--list", action="store_true", help="列出最近的 API Key")
    parser.add_argument("--limit", type=int, default=20, help="列出数量（默认 20）")
    parser.add_argument("--stats", action="store_true", help="显示统计数据")
    parser.add_argument("--export", action="store_true", help="导出为 CSV")
    parser.add_argument("--output", type=str, default="api_keys_export.csv", help="导出文件名")
    parser.add_argument("--disable", type=str, help="禁用指定 API Key")
    parser.add_argument("--enable", type=str, help="启用指定 API Key")
    parser.add_argument("--search", type=str, help="搜索 API Key")
    
    args = parser.parse_args()
    
    if args.list:
        list_keys(args.limit)
    elif args.stats:
        show_stats()
    elif args.export:
        export_csv(args.output)
    elif args.disable:
        disable_key(args.disable)
    elif args.enable:
        enable_key(args.enable)
    elif args.search:
        search_key(args.search)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 db_manager.py --list          # 列出最近 20 条")
        print("  python3 db_manager.py --stats         # 查看统计")
        print("  python3 db_manager.py --export        # 导出 CSV")
        print("  python3 db_manager.py --disable <key> # 禁用 Key")
        print("  python3 db_manager.py --search <tx>   # 搜索交易")

if __name__ == "__main__":
    main()
