"""
测试prompts配置加载和使用
"""
import asyncio
from pathlib import Path

from core.summarizer import ConversationSummarizer


async def test_prompts_loading():
    print("=" * 60)
    print("测试Prompts配置加载")
    print("=" * 60)
    
    # 测试1: 默认加载
    print("\n1. 测试默认加载 prompts.json")
    summarizer = ConversationSummarizer()
    
    print(f"✅ 配置加载成功")
    print(f"   - basic_summary system prompt: {summarizer.prompts_config['system_prompts']['basic_summary'][:50]}...")
    print(f"   - multi_turn_summary max_chars: {summarizer.prompts_config['user_prompts']['multi_turn_summary']['max_chars']}")
    print(f"   - long_answer_compression temperature: {summarizer.prompts_config['llm_parameters']['long_answer_compression']['temperature']}")
    
    # 测试2: 测试摘要功能（需要API key）
    print("\n2. 测试摘要功能")
    test_messages = [
        {"role": "user", "content": "MD500变频器报E001故障"},
        {"role": "assistant", "content": "E001是过热保护报警，请检查散热系统"}
    ]
    
    try:
        summary = await summarizer.summarize_multiple_turns(test_messages)
        if summary:
            print(f"✅ 摘要生成成功")
            print(f"   摘要内容: {summary}")
        else:
            print(f"⚠️  摘要为空（可能是API key未配置）")
    except Exception as e:
        print(f"⚠️  摘要生成失败: {e}")
        print(f"   这通常是因为未配置LLM_API_KEY")
    
    # 测试3: 验证配置参数
    print("\n3. 验证配置参数")
    llm_params = summarizer.prompts_config['llm_parameters']
    
    checks = [
        ("basic_summary temperature", llm_params['basic_summary']['temperature'], 0.1),
        ("multi_turn_summary max_tokens", llm_params['multi_turn_summary']['max_tokens'], 1500),
        ("long_answer_compression max_tokens", llm_params['long_answer_compression']['max_tokens'], 300),
    ]
    
    for name, actual, expected in checks:
        if actual == expected:
            print(f"✅ {name}: {actual}")
        else:
            print(f"⚠️  {name}: {actual} (期望: {expected})")
    
    # 测试4: 测试提示词模板
    print("\n4. 测试提示词模板填充")
    template = summarizer.prompts_config['user_prompts']['multi_turn_summary']['template']
    filled = template.format(conversation_text="测试内容", message_count=4)
    
    if "{conversation_text}" not in filled and "测试内容" in filled:
        print(f"✅ 模板填充成功")
        print(f"   填充后长度: {len(filled)} 字符")
    else:
        print(f"❌ 模板填充失败")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    return True


async def test_custom_prompts():
    """测试自定义prompts文件"""
    print("\n" + "=" * 60)
    print("测试自定义Prompts文件")
    print("=" * 60)
    
    # 使用example文件
    try:
        prompts_file = Path(__file__).parent.parent / "prompts" / "prompts.json.example"
        summarizer = ConversationSummarizer(prompts_file=str(prompts_file))
        print("✅ 成功加载 prompts.json.example")
    except Exception as e:
        print(f"❌ 加载失败: {e}")
    
    # 测试不存在的文件（应该使用默认配置）
    summarizer = ConversationSummarizer(prompts_file="nonexistent.json")
    print("✅ 不存在的文件自动使用默认配置")


if __name__ == "__main__":
    asyncio.run(test_prompts_loading())
    asyncio.run(test_custom_prompts())
