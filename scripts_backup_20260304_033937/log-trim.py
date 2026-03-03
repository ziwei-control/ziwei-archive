#!/usr/bin/env python3
# =============================================================================
# log-trim - 紫微智控日志修剪工具
# 功能：监控日志文件大小，超过阈值自动修剪，保持系统稳定
# 阈值：995MB (保留最后 995MB 内容)
# =============================================================================

import os
import sys
import shutil
import time
from datetime import datetime

# 配置
Ziwei_DIR = "/home/admin/Ziwei"
LOG_DIR = os.path.join(Ziwei_DIR, "data", "logs")
SELF_LEARN_LOG = os.path.join(LOG_DIR, "self_learn.log")
TRIM_LOG = os.path.join(LOG_DIR, "log_trim.log")
MAX_SIZE_MB = 995  # 最大 995MB
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
BACKUP_COUNT = 5  # 保留 5 个备份文件

# 颜色定义
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = "[" + timestamp + "] " + message
    print(log_line)
    
    # 写入修剪日志
    os.makedirs(os.path.dirname(TRIM_LOG), exist_ok=True)
    with open(TRIM_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def get_file_size(filepath):
    """获取文件大小（MB）"""
    if not os.path.exists(filepath):
        return 0
    return os.path.getsize(filepath) / (1024 * 1024)

def trim_log_file():
    """修剪日志文件"""
    if not os.path.exists(SELF_LEARN_LOG):
        log("ℹ️  日志文件不存在：" + SELF_LEARN_LOG)
        return False
    
    current_size = get_file_size(SELF_LEARN_LOG)
    log("📊 当前日志大小：" + str(round(current_size, 2)) + "MB")
    
    # 检查是否需要修剪
    if current_size < MAX_SIZE_MB:
        log("✅ 日志大小正常 (< " + str(MAX_SIZE_MB) + "MB)")
        return False
    
    log("⚠️  日志超过 " + str(MAX_SIZE_MB) + "MB，开始修剪...")
    
    # 备份旧日志
    backup_file = SELF_LEARN_LOG + "." + datetime.now().strftime('%Y%m%d_%H%M%S') + ".bak"
    log("📦 备份日志：" + backup_file)
    shutil.copy2(SELF_LEARN_LOG, backup_file)
    
    # 读取日志内容
    with open(SELF_LEARN_LOG, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    log("📝 总行数：" + str(total_lines))
    
    # 计算需要保留的行数（保留最后 995MB 的内容）
    # 估算：平均每行 100 字节，995MB ≈ 10,430,000 行
    # 为了安全，保留 80%
    avg_line_size = os.path.getsize(SELF_LEARN_LOG) / total_lines if total_lines > 0 else 100
    target_lines = int((MAX_SIZE_MB * 1024 * 1024 * 0.95) / avg_line_size)
    target_lines = max(10000, min(target_lines, total_lines - 1000))  # 至少保留 1 万行，最多删除到剩 1000 行
    
    log("📏 目标保留行数：" + str(target_lines))
    
    # 保留最后的行
    kept_lines = lines[-target_lines:]
    removed_lines = total_lines - target_lines
    
    # 写入修剪后的内容
    with open(SELF_LEARN_LOG, 'w', encoding='utf-8') as f:
        f.writelines(kept_lines)
    
    new_size = get_file_size(SELF_LEARN_LOG)
    log("✅ 修剪完成！")
    log("  删除行数：" + str(removed_lines))
    log("  保留行数：" + str(len(kept_lines)))
    log("  修剪前：" + str(round(current_size, 2)) + "MB")
    log("  修剪后：" + str(round(new_size, 2)) + "MB")
    log("  释放空间：" + str(round(current_size - new_size, 2)) + "MB")
    
    # 清理旧备份（保留最近 5 个）
    cleanup_old_backups()
    
    return True

def cleanup_old_backups():
    """清理旧备份文件"""
    backup_pattern = SELF_LEARN_LOG + ".*\\.bak"
    import glob
    backups = sorted(glob.glob(backup_pattern))
    
    if len(backups) > BACKUP_COUNT:
        log("🧹 清理旧备份（保留最近 " + str(BACKUP_COUNT) + " 个）...")
        for old_backup in backups[:-BACKUP_COUNT]:
            os.remove(old_backup)
            log("  删除：" + old_backup)

def check_all_logs():
    """检查所有日志文件"""
    log("╔════════════════════════════════════════════════════════╗")
    log("║          日志修剪检查                                   ║")
    log("╚════════════════════════════════════════════════════════╝")
    
    if not os.path.exists(LOG_DIR):
        log("⚠️  日志目录不存在：" + LOG_DIR)
        return
    
    # 检查所有 .log 文件
    for filename in os.listdir(LOG_DIR):
        if filename.endswith('.log'):
            filepath = os.path.join(LOG_DIR, filename)
            size = get_file_size(filepath)
            status = "⚠️  警告" if size > MAX_SIZE_MB * 0.9 else "✅"
            log(status + " " + filename + ": " + str(round(size, 2)) + "MB")
    
    log("")
    
    # 特别检查 self_learn.log
    trim_log_file()

def watch_mode(interval=60):
    """监控模式（持续运行）"""
    log("╔════════════════════════════════════════════════════════╗")
    log("║          日志修剪 - 监控模式                            ║")
    log("║          检查间隔：" + str(interval) + "秒                  ║")
    log("║          阈值：" + str(MAX_SIZE_MB) + "MB                   ║")
    log("╚════════════════════════════════════════════════════════╝")
    log("")
    log("👁️  开始 24 小时监控... (Ctrl+C 停止)")
    log("")
    
    check_count = 0
    trim_count = 0
    
    try:
        while True:
            check_count += 1
            current_size = get_file_size(SELF_LEARN_LOG)
            
            # 每 10 次检查输出一次详细日志
            if check_count % 10 == 0:
                log("📊 检查 #" + str(check_count) + " - 当前大小：" + str(round(current_size, 2)) + "MB")
            
            if trim_log_file():
                trim_count += 1
                log("✅ 修剪次数：" + str(trim_count))
            
            time.sleep(interval)
    except KeyboardInterrupt:
        log("")
        log("👋 停止监控")
        log("  总检查次数：" + str(check_count))
        log("  总修剪次数：" + str(trim_count))

def show_status():
    """显示状态"""
    print(Colors.CYAN + "╔════════════════════════════════════════════════════════╗" + Colors.RESET)
    print(Colors.CYAN + "║          日志修剪 - 状态                                ║" + Colors.RESET)
    print(Colors.CYAN + "╚════════════════════════════════════════════════════════╝" + Colors.RESET)
    print()
    
    if os.path.exists(SELF_LEARN_LOG):
        size = get_file_size(SELF_LEARN_LOG)
        percentage = (size / MAX_SIZE_MB) * 100
        
        print("📊 日志文件：" + SELF_LEARN_LOG)
        print("📏 当前大小：" + str(round(size, 2)) + "MB / " + str(MAX_SIZE_MB) + "MB")
        print("📈 使用率：" + str(round(percentage, 2)) + "%")
        print()
        
        if percentage > 90:
            print(Colors.RED + "⚠️  警告：日志大小超过 90%，建议立即修剪！" + Colors.RESET)
        elif percentage > 70:
            print(Colors.YELLOW + "⚠️  注意：日志大小超过 70%，请密切关注" + Colors.RESET)
        else:
            print(Colors.GREEN + "✅ 状态：正常" + Colors.RESET)
    else:
        print("⚠️  日志文件不存在")
    
    print()
    
    # 显示备份文件
    import glob
    backups = glob.glob(SELF_LEARN_LOG + ".*\\.bak")
    if backups:
        print("📦 备份文件：" + str(len(backups)) + "个")
        for backup in sorted(backups)[-5:]:
            backup_size = get_file_size(backup)
            print("   " + os.path.basename(backup) + " (" + str(round(backup_size, 2)) + "MB)")
    
    print()
    
    # 显示修剪历史
    if os.path.exists(TRIM_LOG):
        with open(TRIM_LOG, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        trim_events = [l for l in lines if '修剪完成' in l]
        print("📝 修剪历史：" + str(len(trim_events)) + "次")
        if trim_events:
            print("   最近：" + trim_events[-1].strip())

def show_help():
    """显示帮助"""
    print("log-trim - 紫微智控日志修剪工具 v1.0.0")
    print()
    print("用法：log-trim <命令>")
    print()
    print("命令:")
    print("  check     检查并修剪（一次性）")
    print("  watch     持续监控模式（24 小时运行）")
    print("  status    显示状态")
    print("  trim      立即修剪（不管大小）")
    print("  help      显示帮助")
    print()
    print("参数:")
    print("  --interval <秒>  监控间隔（默认 60 秒）")
    print()
    print("示例:")
    print("  log-trim check")
    print("  log-trim watch --interval 30")
    print("  log-trim status")
    print("  log-trim trim")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    cmd = sys.argv[1].lower()
    
    # 解析参数
    interval = 60
    for i, arg in enumerate(sys.argv):
        if arg == "--interval" and i + 1 < len(sys.argv):
            interval = int(sys.argv[i + 1])
    
    if cmd == "check":
        check_all_logs()
    elif cmd == "watch":
        watch_mode(interval)
    elif cmd == "status":
        show_status()
    elif cmd == "trim":
        log("手动触发修剪...")
        trim_log_file()
    elif cmd == "help":
        show_help()
    else:
        print("未知命令：" + cmd)
        show_help()

if __name__ == "__main__":
    main()
