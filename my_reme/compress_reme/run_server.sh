#!/bin/bash
# 启动 ReMe 压缩服务器的便捷脚本

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

echo "======================================"
echo "启动 ReMe 压缩服务器"
echo "工作目录: $(pwd)"
echo "======================================"

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python"
    exit 1
fi

# 启动服务器
python -m compress_reme.reme_server "$@"
