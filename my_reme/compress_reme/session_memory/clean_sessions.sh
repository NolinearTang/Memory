#!/bin/bash
# 清理所有session数据的脚本

echo "清理session数据..."

# 删除所有session数据
rm -rf .session_memory/messages/*
rm -rf .session_memory/metadata/*

echo "✅ 已清理所有session数据"
echo ""
echo "重启服务后将创建新的session"
