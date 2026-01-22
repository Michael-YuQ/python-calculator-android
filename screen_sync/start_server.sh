#!/bin/bash
# CentOS 服务器启动脚本

echo "=================================="
echo "屏幕同步服务器 - 启动脚本"
echo "=================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，正在安装..."
    sudo yum install -y python3
fi

# 检查端口参数
PORT=${1:-5003}

echo "✅ Python 版本: $(python3 --version)"
echo "📡 监听端口: $PORT"
echo ""

# 启动服务器
python3 server.py $PORT
