"""
测试简化的配置系统
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config


def test_load_config():
    """测试加载配置"""
    print("=" * 60)
    print("测试1: 加载配置")
    print("=" * 60)
    
    kllm_config = get_config()
    
    print(f"✅ 配置类型: {type(kllm_config)}")
    print(f"✅ 配置是字典: {isinstance(kllm_config, dict)}")
    print(f"\n配置的顶级键:")
    for key in kllm_config.keys():
        print(f"  - {key}")


def test_get_model_config():
    """测试获取模型配置"""
    print("\n" + "=" * 60)
    print("测试2: 获取模型配置")
    print("=" * 60)
    
    kllm_config = get_config()
    
    # 获取所有可用模型
    if 'model_hub' in kllm_config:
        models = list(kllm_config['model_hub'].keys())
        print(f"\n可用模型: {models}")
        
        # 获取选中的模型
        selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
        print(f"选中模型: {selected_model}")
        
        # 获取模型配置
        model_config = kllm_config.get('model_hub', {}).get(selected_model)
        if model_config:
            print(f"\n{selected_model} 模型配置:")
            for key, value in model_config.items():
                if key == 'api_key' and value:
                    value = f"{value[:10]}..."
                print(f"  {key}: {value}")
        else:
            print(f"❌ 未找到模型配置: {selected_model}")
    else:
        print("❌ 配置中没有 model_hub")


def test_get_other_config():
    """测试获取其他配置"""
    print("\n" + "=" * 60)
    print("测试3: 获取其他配置")
    print("=" * 60)
    
    kllm_config = get_config()
    
    # 存储配置
    storage_config = kllm_config.get('storage', {})
    if storage_config:
        print(f"\n存储配置:")
        print(f"  目录: {storage_config.get('dir')}")
        print(f"  消息子目录: {storage_config.get('messages_subdir')}")
        print(f"  元数据子目录: {storage_config.get('metadata_subdir')}")
    
    # Session配置
    session_config = kllm_config.get('session', {})
    if session_config:
        print(f"\nSession配置:")
        print(f"  保留最近: {session_config.get('keep_recent')}")
        print(f"  压缩阈值: {session_config.get('compress_threshold')}")
        print(f"  摘要触发: {session_config.get('max_turns_before_summary')}")
    
    # 检索配置
    retrieval_config = kllm_config.get('retrieval', {})
    if retrieval_config:
        bm25_config = retrieval_config.get('bm25', {})
        print(f"\nBM25检索配置:")
        print(f"  k1: {bm25_config.get('k1')}")
        print(f"  b: {bm25_config.get('b')}")
        print(f"  top_k: {bm25_config.get('top_k')}")


def test_dict_operations():
    """测试字典操作"""
    print("\n" + "=" * 60)
    print("测试4: 字典操作")
    print("=" * 60)
    
    kllm_config = get_config()
    
    # 测试in操作
    print(f"\n'model_hub' in kllm_config: {'model_hub' in kllm_config}")
    print(f"'llm' in kllm_config: {'llm' in kllm_config}")
    
    # 测试get操作（安全）
    value1 = kllm_config.get('llm', {}).get('selected_model', 'default')
    print(f"\nget操作结果: {value1}")
    
    # 测试keys(), values(), items()
    print(f"\n配置的所有键: {list(kllm_config.keys())}")
    
    # 遍历model_hub
    if 'model_hub' in kllm_config:
        print(f"\n遍历model_hub:")
        for model_name, model_config in kllm_config['model_hub'].items():
            model_display_name = model_config.get('model_name', 'N/A')
            print(f"  {model_name} -> {model_display_name}")


def test_usage_example():
    """测试实际使用示例"""
    print("\n" + "=" * 60)
    print("测试5: 实际使用示例")
    print("=" * 60)
    
    kllm_config = get_config()
    
    # 示例：获取模型配置并准备初始化LLM
    print("\n模拟LLM客户端初始化:")
    
    # 步骤1: 获取选中的模型
    selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
    print(f"1. 选中模型: {selected_model}")
    
    # 步骤2: 获取模型配置
    model_config = kllm_config.get('model_hub', {}).get(selected_model)
    if model_config:
        print(f"2. 模型配置获取成功")
        
        # 步骤3: 提取需要的参数
        print(f"3. 模型参数:")
        print(f"   - model_name: {model_config.get('model_name')}")
        print(f"   - temperature: {model_config.get('temperature')}")
        print(f"   - max_tokens: {model_config.get('max_tokens')}")
        print(f"   - timeout: {model_config.get('timeout')}")
        
        # 这里就可以传给LlmClient了
        print(f"\n✅ 配置ready，可以初始化 LlmClient(model_config)")
    else:
        print(f"❌ 模型配置不存在: {selected_model}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("简化配置系统测试")
    print("=" * 60)
    
    try:
        test_load_config()
        test_get_model_config()
        test_get_other_config()
        test_dict_operations()
        test_usage_example()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
        print("\n💡 使用方式:")
        print("   from config import get_config")
        print("   kllm_config = get_config()")
        print("   model_config = kllm_config['model_hub']['gpt4']")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
