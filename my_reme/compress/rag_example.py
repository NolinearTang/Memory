"""RAG检索内容压缩示例

演示如何压缩向量数据库检索结果，节省RAG应用的token使用。
"""

from compress.client import CompressClient


def example_basic_rag():
    """基础RAG压缩示例"""
    print("=" * 70)
    print("示例 1: 基础RAG压缩")
    print("=" * 70)
    
    client = CompressClient()
    
    # 模拟向量数据库检索到的文档
    documents = [
        {
            "content": "Python是一种高级编程语言，以其简洁易读的语法著称。Python支持多种编程范式，包括面向对象、命令式和函数式编程。",
            "score": 0.92,
            "metadata": {"source": "python_basics.txt", "page": 1}
        },
        {
            "content": "Python在数据科学、机器学习、Web开发等领域都有广泛应用。常用的库包括NumPy、Pandas、TensorFlow等。",
            "score": 0.85,
            "metadata": {"source": "python_applications.txt", "page": 3}
        },
        {
            "content": "Python 3.11相比之前的版本提供了显著的性能提升，执行速度提高了10-60%。",
            "score": 0.78,
            "metadata": {"source": "python_news.txt", "page": 12}
        },
    ]
    
    query = "什么是Python？"
    
    # 压缩RAG结果
    result = client.compress_rag(
        documents=documents,
        query=query,
        model="gpt-4o"
    )
    
    print(f"查询: {query}")
    print(f"检索到文档数: {result['original_count']}")
    print(f"保留文档数: {result['compressed_count']}")
    print(f"Token节省: {result['tokens_before']} → {result['tokens_after']} ({result['compression_ratio']:.1%})")
    print()


def example_filter_by_score():
    """按相关性分数过滤"""
    print("=" * 70)
    print("示例 2: 按相关性分数过滤低质量文档")
    print("=" * 70)
    
    client = CompressClient()
    
    # 包含不同质量的检索结果
    documents = [
        {"content": "高度相关的内容 " * 50, "score": 0.95},
        {"content": "相关的内容 " * 50, "score": 0.82},
        {"content": "中等相关的内容 " * 50, "score": 0.65},
        {"content": "弱相关的内容 " * 50, "score": 0.45},
        {"content": "几乎不相关的内容 " * 50, "score": 0.25},
    ]
    
    query = "示例查询"
    
    # 只保留分数>0.6的文档
    result = client.compress_rag(
        documents=documents,
        query=query,
        min_score=0.6,  # 过滤阈值
        model="gpt-4o"
    )
    
    print(f"原始文档数: {result['original_count']}")
    print(f"过滤后保留: {result['compressed_count']} 个文档 (min_score=0.6)")
    print(f"保留的文档分数: {[doc['score'] for doc in result['documents']]}")
    print()


def example_top_k():
    """保留Top-K最相关的文档"""
    print("=" * 70)
    print("示例 3: 保留Top-K最相关的文档")
    print("=" * 70)
    
    client = CompressClient()
    
    # 生成10个文档
    documents = [
        {"content": f"文档{i}的内容 " * 30, "score": 0.9 - i * 0.08}
        for i in range(10)
    ]
    
    query = "查询内容"
    
    # 只保留前3个最相关的
    result = client.compress_rag(
        documents=documents,
        query=query,
        top_k=3,
        model="gpt-4o"
    )
    
    print(f"原始文档数: {result['original_count']}")
    print(f"保留Top-{3}: {result['compressed_count']} 个文档")
    scores = [f"{doc['score']:.2f}" for doc in result['documents']]
    print(f"保留的文档分数: {scores}")
    print()


def example_aggressive_compression():
    """激进压缩：处理超长文档"""
    print("=" * 70)
    print("示例 4: 激进压缩超长文档")
    print("=" * 70)
    
    client = CompressClient()
    
    # 模拟超长文档
    documents = [
        {
            "content": "这是一份非常详细的技术文档。" * 500,  # 超长内容
            "score": 0.95,
            "metadata": {"source": "long_doc.pdf", "pages": "1-50"}
        },
    ]
    
    query = "总结这份文档"
    
    # 激进压缩：只保留10%
    result = client.compress_rag(
        documents=documents,
        query=query,
        target_ratio=0.1,  # 只保留10%
        model="gpt-4o"
    )
    
    doc = result['documents'][0]
    print(f"原始文档长度: {doc['original_length']:,} 字符")
    print(f"压缩后长度: {doc['compressed_length']:,} 字符")
    print(f"压缩比: {doc['compressed_length'] / doc['original_length']:.1%}")
    print(f"Token节省: {result['tokens_saved']:,}")
    print()


def example_real_rag_workflow():
    """真实RAG工作流示例"""
    print("=" * 70)
    print("示例 5: 完整RAG工作流（模拟）")
    print("=" * 70)
    
    client = CompressClient()
    
    # 步骤1: 模拟向量数据库检索（这里是模拟数据）
    print("步骤1: 向量数据库检索...")
    vector_search_results = [
        {
            "content": "FastAPI是一个现代、快速的Web框架，用于构建API。它基于Python 3.7+的类型提示，提供自动API文档生成、数据验证等功能。FastAPI的性能可与NodeJS和Go媲美。",
            "score": 0.94,
            "metadata": {"doc_id": "doc_001", "source": "fastapi_intro.md", "chunk_id": 5}
        },
        {
            "content": "FastAPI支持异步编程，使用async/await语法。它内置了OpenAPI和JSON Schema支持，可以自动生成交互式API文档（Swagger UI）。",
            "score": 0.89,
            "metadata": {"doc_id": "doc_001", "source": "fastapi_intro.md", "chunk_id": 12}
        },
        {
            "content": "要开始使用FastAPI，首先需要安装：pip install fastapi uvicorn。创建一个简单的应用只需要几行代码。FastAPI会自动进行请求验证和序列化。",
            "score": 0.82,
            "metadata": {"doc_id": "doc_002", "source": "fastapi_quickstart.md", "chunk_id": 3}
        },
        {
            "content": "Django是另一个流行的Python Web框架，采用MTV架构模式。Django提供了完整的ORM、管理后台、认证系统等功能。",
            "score": 0.65,
            "metadata": {"doc_id": "doc_003", "source": "django_guide.md", "chunk_id": 1}
        },
        {
            "content": "Flask是一个轻量级的WSGI Web应用框架。Flask的设计哲学是保持核心简单但可扩展。",
            "score": 0.58,
            "metadata": {"doc_id": "doc_004", "source": "flask_basics.md", "chunk_id": 2}
        },
    ]
    
    user_query = "如何使用FastAPI构建API？"
    print(f"用户查询: '{user_query}'")
    print(f"检索到 {len(vector_search_results)} 个文档块")
    
    # 步骤2: 压缩检索结果
    print("\n步骤2: 压缩检索结果...")
    result = client.compress_rag(
        documents=vector_search_results,
        query=user_query,
        top_k=3,           # 只保留最相关的3个
        min_score=0.7,     # 过滤低分文档
        target_ratio=0.3,  # 压缩到30%
        model="gpt-4o",
        preserve_metadata=True
    )
    
    print(f"保留文档数: {result['compressed_count']}")
    print(f"Token节省: {result['tokens_saved']:,} ({result['compression_ratio']:.1%})")
    
    # 步骤3: 构建最终的LLM prompt
    print("\n步骤3: 构建LLM prompt...")
    context = "\n\n".join([
        f"[文档 {i+1}] (来源: {doc.get('metadata', {}).get('source', 'unknown')})\n{doc['content']}"
        for i, doc in enumerate(result['documents'])
    ])
    
    final_prompt = f"""基于以下文档回答问题。

问题: {user_query}

相关文档:
{context}

请提供详细的回答："""
    
    print(f"最终prompt长度: {len(final_prompt)} 字符")
    print(f"预估token数: ~{len(final_prompt) // 4}")  # 粗略估算
    
    # 步骤4: 发送给LLM（这里只是演示，不实际调用）
    print("\n步骤4: 发送给LLM...")
    print("✅ 压缩后的上下文已准备好，可以发送给LLM进行推理")
    
    print(f"\n压缩效果总结:")
    print(f"  - 原始检索: {len(vector_search_results)} 个文档")
    print(f"  - 过滤后: {result['compressed_count']} 个文档")
    print(f"  - Token节省: {result['tokens_saved']:,} ({result['compression_ratio']:.1%})")
    print()


def example_batch_rag():
    """批量处理多个查询的RAG结果"""
    print("=" * 70)
    print("示例 6: 批量压缩RAG结果")
    print("=" * 70)
    
    client = CompressClient()
    
    # 模拟多个用户查询
    queries = [
        "什么是Python？",
        "如何使用FastAPI？",
        "机器学习的基础知识"
    ]
    
    total_saved = 0
    
    for i, query in enumerate(queries, 1):
        # 每个查询的检索结果（这里用相同的模拟数据）
        documents = [
            {"content": f"关于'{query}'的内容 " * 50, "score": 0.9 - j * 0.1}
            for j in range(5)
        ]
        
        result = client.compress_rag(
            documents=documents,
            query=query,
            top_k=3,
            model="gpt-4o"
        )
        
        total_saved += result['tokens_saved']
        print(f"查询 {i}: '{query}'")
        print(f"  节省: {result['tokens_saved']:,} tokens")
    
    print(f"\n批量处理总节省: {total_saved:,} tokens")
    print()


def main():
    """运行所有RAG示例"""
    try:
        example_basic_rag()
        example_filter_by_score()
        example_top_k()
        example_aggressive_compression()
        example_real_rag_workflow()
        example_batch_rag()
        
        print("=" * 70)
        print("✅ 所有RAG示例运行完成！")
        print("=" * 70)
        
        # 查看总体统计
        client = CompressClient()
        client.print_stats()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保服务器正在运行：")
        print("  python -m compress.compress_server")


if __name__ == "__main__":
    main()
