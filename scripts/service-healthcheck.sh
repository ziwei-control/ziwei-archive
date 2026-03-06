#!/bin/bash
# =============================================================================
# 紫微智控 - 服务健康检查脚本
# 用法：./service-healthcheck.sh
# =============================================================================

echo "=========================================="
echo "  紫微智控 - 服务健康检查"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Supervisor 服务状态
echo "【Supervisor 服务状态】"
echo "------------------------------------------"
supervisorctl status | while read line; do
    if echo "$line" | grep -q "RUNNING"; then
        echo -e "${GREEN}✓${NC} $line"
    elif echo "$line" | grep -q "FATAL\|STOPPED\|BACKOFF"; then
        echo -e "${RED}✗${NC} $line"
    else
        echo -e "${YELLOW}⚠${NC} $line"
    fi
done
echo ""

# 检查重复进程
echo "【重复进程检查】"
echo "------------------------------------------"
for service in "dashboard_v3_framer" "global-warroom" "log-trim"; do
    count=$(ps aux | grep "$service" | grep -v grep | wc -l)
    if [ "$count" -gt 1 ]; then
        echo -e "${RED}✗${NC} $service: $count 个进程 (异常)"
    else
        echo -e "${GREEN}✓${NC} $service: $count 个进程"
    fi
done
echo ""

# 检查 Dashboard 可访问性
echo "【Dashboard 访问测试】"
echo "------------------------------------------"
if timeout 10 curl -s http://localhost:8081/ | grep -q "<title>"; then
    echo -e "${GREEN}✓${NC} 本地访问：正常"
else
    echo -e "${RED}✗${NC} 本地访问：失败"
fi

if timeout 10 curl -s http://localhost:8081/ | grep -q "<title>"; then
    echo -e "${GREEN}✓${NC} 公网访问：正常"
else
    echo -e "${YELLOW}⚠${NC} 公网访问：超时 (检查防火墙/端口转发)"
fi

# 检查 CLI API
echo ""
echo "【CLI API 测试】"
echo "------------------------------------------"
cli_result=$(timeout 5 curl -s -X POST http://localhost:8081/api/execute -H "Content-Type: application/json" -d '{"command": "echo test"}' 2>/dev/null)
if echo "$cli_result" | grep -q '"success": true'; then
    echo -e "${GREEN}✓${NC} CLI API: 正常"
else
    echo -e "${RED}✗${NC} CLI API: 失败"
fi
echo ""

# 检查端口占用
echo "【端口占用检查】"
echo "------------------------------------------"
for port in 8081 9001; do
    pid=$(lsof -i :$port 2>/dev/null | grep LISTEN | awk '{print $2}')
    if [ -n "$pid" ]; then
        echo -e "${GREEN}✓${NC} 端口 $port: 已占用 (PID: $pid)"
    else
        echo -e "${RED}✗${NC} 端口 $port: 未占用"
    fi
done
echo ""

# 总结
echo "=========================================="
echo "  健康检查完成"
echo "=========================================="

# 如果有 FATAL 服务，提示修复命令
fatal_count=$(supervisorctl status | grep -c "FATAL\|STOPPED\|BACKOFF")
if [ "$fatal_count" -gt 0 ]; then
    echo ""
    echo -e "${RED}发现 $fatal_count 个异常服务！${NC}"
    echo "修复命令:"
    echo "  supervisorctl restart all"
    echo "  # 或重启单个服务:"
    echo "  supervisorctl restart ziwei-dashboard"
fi
