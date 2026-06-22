"""
测试所有导入路径是否正确
"""

def test_imports():
    """测试所有模块的导入"""
    
    print("=" * 60)
    print("测试导入路径")
    print("=" * 60)
    
    # 测试核心模块导入
    print("\n1. 测试核心模块导入")
    try:
        from core.models import Message, SessionData
        from core.storage import SessionStorage
        from core.session_manager import SessionMemoryManager
        from core.summarizer import ConversationSummarizer
        from core.llm_client import LlmClient
        print("   ✅ 核心模块导入成功")
    except ImportError as e:
        print(f"   ❌ 核心模块导入失败: {e}")
        return False
    
    # 测试检索模块导入
    print("\n2. 测试检索模块导入")
    try:
        from retrieval.bm25_retriever import BM25Retriever
        print("   ✅ 检索模块导入成功")
    except ImportError as e:
        print(f"   ❌ 检索模块导入失败: {e}")
        return False
    
    # 测试配置模块导入
    print("\n3. 测试配置模块导入")
    try:
        from config import Config, get_config, reload_config, get_value
        from config.config import Config as ConfigClass
        print("   ✅ 配置模块导入成功")
    except ImportError as e:
        print(f"   ❌ 配置模块导入失败: {e}")
        return False
    
    # 测试主模块导入
    print("\n4. 测试主模块导入（通过__init__.py）")
    try:
        import __init__
        print(f"   ✅ 版本号: {__init__.__version__}")
    except ImportError as e:
        print(f"   ❌ 主模块导入失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 所有导入测试通过！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
