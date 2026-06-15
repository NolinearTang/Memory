#!/usr/bin/env python
"""验证 compress_reme 项目结构

检查重构后的文件结构是否正确。
"""

import os
from pathlib import Path


def verify_structure():
    """验证项目结构"""
    
    print("=" * 70)
    print("验证 compress_reme 项目结构")
    print("=" * 70)
    print()
    
    # 必需的目录
    required_dirs = [
        "compress_reme",
        "compress_reme/core",
        "compress_reme/server",
        "compress_reme/client",
        "examples",
        "tests",
        "docs",
        "scripts",
    ]
    
    # 必需的文件
    required_files = {
        # 主代码
        "compress_reme/__init__.py": "主包初始化",
        "compress_reme/__main__.py": "入口文件",
        "compress_reme/core/__init__.py": "核心模块",
        "compress_reme/core/models.py": "数据模型",
        "compress_reme/core/session_manager.py": "Session管理",
        "compress_reme/server/__init__.py": "服务器模块",
        "compress_reme/server/app.py": "FastAPI应用",
        "compress_reme/client/__init__.py": "客户端模块",
        "compress_reme/client/client.py": "Python SDK",
        # 示例
        "examples/__init__.py": "示例包",
        "examples/basic_usage.py": "基础示例",
        "examples/config_example.py": "配置示例",
        # 测试
        "tests/__init__.py": "测试包",
        "tests/test_install.py": "安装测试",
        # 文档
        "docs/README.md": "详细文档",
        "docs/QUICKSTART.md": "快速开始",
        "docs/PROJECT.md": "项目概览",
        "docs/CONFIG_GUIDE.md": "配置指南",
        # 脚本
        "scripts/run_server.sh": "Unix脚本",
        "scripts/run_server.bat": "Windows脚本",
        # 配置
        "README.md": "项目主README",
        "STRUCTURE.md": "结构说明",
        "MIGRATION.md": "迁移指南",
        "pyproject.toml": "项目配置",
        "requirements.txt": "依赖列表",
        ".gitignore": "Git忽略",
    }
    
    all_good = True
    
    # 检查目录
    print("📁 检查目录结构...")
    print()
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.is_dir():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ - 不存在")
            all_good = False
    
    print()
    
    # 检查文件
    print("📄 检查必需文件...")
    print()
    for file_path, description in required_files.items():
        full_path = Path(file_path)
        if full_path.is_file():
            size = full_path.stat().st_size
            print(f"  ✅ {file_path:45s} ({size:>6} bytes) - {description}")
        else:
            print(f"  ❌ {file_path:45s} - {description} [不存在]")
            all_good = False
    
    print()
    print("=" * 70)
    
    # 检查导入
    print("\n🔍 检查包导入...")
    print()
    
    import_tests = [
        ("compress_reme", "主包"),
        ("compress_reme.core", "核心模块"),
        ("compress_reme.server", "服务器模块"),
        ("compress_reme.client", "客户端模块"),
    ]
    
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name:30s} - {description}")
        except ImportError as e:
            print(f"  ❌ {module_name:30s} - {description} [导入失败: {e}]")
            all_good = False
    
    # 检查顶层导入
    print()
    try:
        from compress_reme import ReMeClient, SessionManager, SessionInfo
        print("  ✅ 顶层导入成功:")
        print(f"     - ReMeClient: {ReMeClient}")
        print(f"     - SessionManager: {SessionManager}")
        print(f"     - SessionInfo: {SessionInfo}")
    except ImportError as e:
        print(f"  ❌ 顶层导入失败: {e}")
        all_good = False
    
    print()
    print("=" * 70)
    
    # 统计信息
    print("\n📊 统计信息...")
    print()
    
    # 统计代码行数
    total_lines = 0
    total_files = 0
    
    for file_path in required_files.keys():
        if file_path.endswith('.py'):
            full_path = Path(file_path)
            if full_path.is_file():
                lines = len(full_path.read_text().splitlines())
                total_lines += lines
                total_files += 1
    
    print(f"  Python 文件数: {total_files}")
    print(f"  总代码行数: {total_lines}")
    
    print()
    print("=" * 70)
    
    # 最终结果
    print()
    if all_good:
        print("🎉 项目结构验证通过！")
        print()
        print("✅ 所有目录和文件就位")
        print("✅ 所有模块可以正常导入")
        print("✅ 项目已准备就绪")
        print()
        print("下一步:")
        print("  1. pip install -e .")
        print("  2. python -m compress_reme")
        print("  3. 访问 http://localhost:8788/docs")
        return 0
    else:
        print("⚠️  项目结构验证失败！")
        print()
        print("请检查上面标记为 ❌ 的项目")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(verify_structure())
