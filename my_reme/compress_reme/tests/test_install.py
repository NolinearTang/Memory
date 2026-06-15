#!/usr/bin/env python
"""测试安装是否正确

验证所有依赖是否已正确安装。
"""

import sys


def test_imports():
    """测试导入"""
    print("=" * 60)
    print("测试依赖安装")
    print("=" * 60)
    
    tests = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Requests", "requests"),
        ("Pydantic", "pydantic"),
        ("AgentScope", "agentscope"),
        ("ReMe", "reme"),
    ]
    
    all_passed = True
    
    for name, module in tests:
        try:
            __import__(module)
            print(f"✅ {name:20s} - 已安装")
        except ImportError as e:
            print(f"❌ {name:20s} - 未安装: {e}")
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ 所有依赖已正确安装！")
        print("\n可以运行:")
        print("  python -m compress_reme.reme_server")
        return 0
    else:
        print("❌ 部分依赖未安装")
        print("\n请运行:")
        print("  pip install -r requirements.txt")
        print("\n或:")
        print("  pip install -e .")
        return 1


def test_compress_reme():
    """测试 compress_reme 包"""
    print("\n" + "=" * 60)
    print("测试 compress_reme 包")
    print("=" * 60)
    
    try:
        from compress_reme import ReMeClient, SessionManager
        print("✅ compress_reme 包导入成功")
        print(f"   - ReMeClient: {ReMeClient}")
        print(f"   - SessionManager: {SessionManager}")
        return True
    except ImportError as e:
        print(f"❌ compress_reme 包导入失败: {e}")
        print("\n请确保在 compress_reme 目录下运行")
        return False


def main():
    """主函数"""
    import_ok = test_imports()
    package_ok = test_compress_reme()
    
    print("\n" + "=" * 60)
    if import_ok == 0 and package_ok:
        print("🎉 安装测试通过！可以开始使用了")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 启动服务器: python -m compress_reme.reme_server")
        print("  2. 运行示例:   python -m compress_reme.example")
        print("  3. 查看文档:   cat README.md")
        return 0
    else:
        print("⚠️ 请先完成安装")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
