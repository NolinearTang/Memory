"""压缩服务使用示例

演示如何使用 Headroom 压缩服务。
"""

import json
from compress.client import CompressClient


def example_basic():
    """基础示例：压缩简单消息"""
    print("=" * 60)
    print("示例 1: 基础压缩")
    print("=" * 60)
    
    client = CompressClient()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请介绍一下 Python 编程语言。"},
    ]
    
    result = client.compress(messages, model="gpt-4o")
    
    print(f"压缩前: {result['tokens_before']} tokens")
    print(f"压缩后: {result['tokens_after']} tokens")
    print(f"节省:   {result['tokens_saved']} tokens ({result['compression_ratio']:.1%})")
    print()


def example_large_tool_result():
    """示例 2: 压缩大型工具输出"""
    print("=" * 60)
    print("示例 2: 压缩大型工具输出")
    print("=" * 60)
    
    client = CompressClient()
    
    # 模拟大量搜索结果
    messages = [
        {"role": "system", "content": "You analyze search results."},
        {"role": "user", "content": "Search for Python tutorials."},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_1",
                "type": "function",
                "function": {"name": "search", "arguments": '{"q": "python"}'},
            }],
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "content": json.dumps({
                "results": [
                    {
                        "title": f"Python Tutorial {i}",
                        "snippet": f"Learn Python programming with example {i}. " * 10,
                        "url": f"https://example.com/tutorial-{i}",
                        "score": 100 - i,
                    }
                    for i in range(500)  # 500 条搜索结果
                ]
            }),
        },
        {"role": "user", "content": "What are the top 3 results?"},
    ]
    
    result = client.compress(messages, model="gpt-4o")
    
    print(f"压缩前: {result['tokens_before']:,} tokens")
    print(f"压缩后: {result['tokens_after']:,} tokens")
    print(f"节省:   {result['tokens_saved']:,} tokens ({result['compression_ratio']:.1%})")
    print(f"应用的压缩器: {', '.join(result['transforms_applied'])}")
    print()


def example_custom_ratio():
    """示例 3: 自定义压缩比"""
    print("=" * 60)
    print("示例 3: 自定义压缩比")
    print("=" * 60)
    
    client = CompressClient()
    
    messages = [
        {"role": "user", "content": "This is a long message. " * 100},
    ]
    
    # 保守压缩：保留 70%
    result1 = client.compress(messages, model="gpt-4o", target_ratio=0.7)
    print(f"保留 70%: {result1['tokens_before']} → {result1['tokens_after']} tokens")
    
    # 激进压缩：保留 20%
    result2 = client.compress(messages, model="gpt-4o", target_ratio=0.2)
    print(f"保留 20%: {result2['tokens_before']} → {result2['tokens_after']} tokens")
    
    # 自动决策
    result3 = client.compress(messages, model="gpt-4o")
    print(f"自动决策: {result3['tokens_before']} → {result3['tokens_after']} tokens")
    print()


def example_disable_ml():
    """示例 4: 禁用 ML 压缩"""
    print("=" * 60)
    print("示例 4: 禁用 ML 压缩（仅规则压缩）")
    print("=" * 60)
    
    client = CompressClient()
    
    messages = [
        {
            "role": "tool",
            "content": json.dumps({
                "results": [{"id": i, "value": f"item_{i}"} for i in range(100)]
            }),
        },
    ]
    
    # 使用 ML 压缩
    result1 = client.compress(messages, model="gpt-4o")
    print(f"ML 压缩:   {result1['tokens_saved']} tokens saved")
    print(f"  应用: {', '.join(result1['transforms_applied'])}")
    
    # 禁用 ML 压缩
    result2 = client.compress(messages, model="gpt-4o", kompress_model="disabled")
    print(f"规则压缩: {result2['tokens_saved']} tokens saved")
    print(f"  应用: {', '.join(result2['transforms_applied'])}")
    print()


def example_integration():
    """示例 5: 与 LLM API 集成"""
    print("=" * 60)
    print("示例 5: 与 LLM API 集成")
    print("=" * 60)
    
    client = CompressClient()
    
    # 准备消息
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请总结以下内容：" + "一些很长的文本内容... " * 100},
    ]
    
    # 压缩
    result = client.compress(messages, model="qwen-plus")
    
    print(f"压缩节省: {result['tokens_saved']} tokens")
    
    # 现在可以使用 result['messages'] 调用你的 LLM API
    # compressed_messages = result['messages']
    # response = your_llm_api.chat(messages=compressed_messages)
    
    print("✅ 压缩后的消息可以直接发送给 LLM API")
    print()


def example_rag_compression():
    """示例 6: 压缩RAG检索内容"""
    print("=" * 60)
    print("示例 6: 压缩RAG检索内容")
    print("=" * 60)
    
    client = CompressClient()
    
    # 模拟向量数据库检索结果
    documents = [
        {
            "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. " * 20,
            "score": 0.95,
            "metadata": {"source": "python_intro.txt", "title": "Python Introduction", "page": 1}
        },
        {
            "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. " * 15,
            "score": 0.88,
            "metadata": {"source": "fastapi_guide.txt", "title": "FastAPI Guide", "page": 5}
        },
        {
            "content": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. " * 10,
            "score": 0.72,
            "metadata": {"source": "django_docs.txt", "title": "Django Documentation", "page": 3}
        },
        {
            "content": "Flask is a lightweight WSGI web application framework in Python designed with simplicity in mind. " * 8,
            "score": 0.65,
            "metadata": {"source": "flask_tutorial.txt", "title": "Flask Tutorial", "page": 2}
        },
        {
            "content": "NumPy is a fundamental package for scientific computing in Python, providing support for arrays and matrices. " * 5,
            "score": 0.45,
            "metadata": {"source": "numpy_basics.txt", "title": "NumPy Basics", "page": 10}
        },
    ]
    
    query = "What is Python and what frameworks are available?"
    
    # 压缩RAG结果
    result = client.compress_rag(
        documents=documents,
        query=query,
        top_k=3,           # 只保留前3个最相关的文档
        min_score=0.5,     # 过滤掉分数低于0.5的文档
        target_ratio=0.3,  # 每个文档压缩到30%
        model="gpt-4o"
    )
    
    print(f"原始文档数: {result['original_count']}")
    print(f"压缩后文档数: {result['compressed_count']}")
    print(f"Tokens: {result['tokens_before']:,} → {result['tokens_after']:,}")
    print(f"节省: {result['tokens_saved']:,} tokens ({result['compression_ratio']:.1%})")
    print(f"\n压缩后的文档:")
    for i, doc in enumerate(result['documents'], 1):
        print(f"  [{i}] Score: {doc['score']:.2f}")
        print(f"      原始长度: {doc['original_length']}, 压缩后: {doc['compressed_length']}")
        if 'metadata' in doc:
            print(f"      来源: {doc['metadata'].get('source', 'N/A')}")
        print(f"      内容预览: {doc['content'][:100]}...")
    print()


def example_stats():
    """示例 7: 查看统计信息"""
    print("=" * 60)
    print("示例 7: 统计信息")
    print("=" * 60)
    
    client = CompressClient()
    
    # 打印格式化的统计
    client.print_stats()


def main():
    """运行所有示例"""
    try:
        example_basic()
        example_large_tool_result()
        example_custom_ratio()
        example_disable_ml()
        example_integration()
        example_rag_compression()
        example_stats()
        
        print("\n✅ 所有示例运行完成！")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保服务器正在运行：")
        print("  python -m compress.compress_server")


if __name__ == "__main__":
    main()
