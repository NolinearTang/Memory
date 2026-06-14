@echo off
REM 启动 ReMe 压缩服务器的便捷脚本 (Windows)

cd /d "%~dp0"

echo ======================================
echo 启动 ReMe 压缩服务器
echo 工作目录: %CD%
echo ======================================

python -m compress_reme.reme_server %*
