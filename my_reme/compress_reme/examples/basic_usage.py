"""ReMe压缩服务使用示例

演示如何使用ReMe服务进行对话压缩和记忆抽取。
"""

import time

from compress_reme.client import ReMeClient


def example_basic_workflow():
    """基础工作流示例"""
    print("=" * 70)
    print("示例 1: 基础工作流")
    print("=" * 70)
    
    client = ReMeClient()
    
    # 创建会话
    session_id = "demo_session_001"
    print(f"\n1. 创建会话: {session_id}")
    result = client.create_session(session_id)
    print(f"   状态: {result['status']}")
    
    # 添加对话消息
    print(f"\n2. 添加对话消息...")
    messages = [
        {"role": "user", "content": "你好，我想学习Python编程。"},
        {"role": "assistant", "content": "很高兴为你介绍Python！Python是一种非常适合初学者的编程语言。"},
        {"role": "user", "content": "它有什么特点？"},
        {"role": "assistant", "content": "Python的主要特点包括：1. 语法简洁清晰 2. 丰富的库生态 3. 跨平台支持 4. 强大的社区支持。"},
    ]
    result = client.add_messages(session_id, messages)
    print(f"   添加了 {result['message_count']} 条消息")
    
    # 获取消息
    print(f"\n3. 获取会话消息...")
    result = client.get_messages(session_id, limit=2)
    print(f"   总消息数: {result['total_count']}")
    print(f"   最近2条消息:")
    for msg in result['messages'][-2:]:
        print(f"     [{msg['role']}]: {msg['content'][:50]}...")
    
    # 压缩对话
    print(f"\n4. 压缩对话...")
    result = client.compact(session_id)
    print(f"   压缩前: {result['tokens_before']:,} tokens")
    print(f"   压缩后: {result['tokens_after']:,} tokens")
    print(f"   节省: {result['tokens_saved']:,} tokens")
    
    # 清理
    client.delete_session(session_id)
    print(f"\n会话已删除")
    print()


def example_long_conversation():
    """长对话压缩示例"""
    print("=" * 70)
    print("示例 2: 长对话压缩")
    print("=" * 70)
    
    client = ReMeClient()
    
    session_id = "long_conv_session"
    client.create_session(session_id)
    
    # 模拟长对话
    print(f"\n模拟长对话 (30轮)...")
    for i in range(30):
        messages = [
            {"role": "user", "content": f"这是第{i+1}轮对话的用户消息。" + "内容较长。" * 20},
            {"role": "assistant", "content": f"这是第{i+1}轮对话的助手回复。" + "详细的回复内容。" * 30},
        ]
        client.add_messages(session_id, messages)
    
    print(f"   已添加 60 条消息")
    
    # 压缩前统计
    stats_before = client.get_session_stats(session_id)
    print(f"\n压缩前统计:")
    print(f"   消息数: {stats_before['message_count']}")
    print(f"   Token数: {stats_before['total_tokens']:,}")
    
    # 执行压缩
    print(f"\n执行压缩...")
    result = client.compact(session_id, compact_type="auto")
    print(f"   节省: {result['tokens_saved']:,} tokens ({result['compression_ratio']:.1%})")
    
    # 清理
    client.delete_session(session_id)
    print()


def example_summary_generation():
    """摘要生成示例"""
    print("=" * 70)
    print("示例 3: 对话摘要生成")
    print("=" * 70)
    
    client = ReMeClient()
    
    session_id = "summary_session"
    client.create_session(session_id)
    
    # 添加一段对话
    print(f"\n添加对话内容...")
    messages = [
        {"role": "user", "content": "请介绍一下机器学习的基础知识。"},
        {"role": "assistant", "content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策。主要分为监督学习、无监督学习和强化学习三大类。" * 10},
        {"role": "user", "content": "监督学习有哪些应用场景？"},
        {"role": "assistant", "content": "监督学习的应用非常广泛，包括图像识别、语音识别、垃圾邮件过滤、医疗诊断等。它通过标注数据来训练模型，使模型能够对新数据进行预测。" * 10},
        {"role": "user", "content": "推荐一些学习资源？"},
        {"role": "assistant", "content": "推荐的学习资源包括Andrew Ng的机器学习课程、《统计学习方法》这本书，以及Kaggle平台上的实战项目。" * 10},
    ]
    client.add_messages(session_id, messages)
    
    # 生成摘要
    print(f"\n生成对话摘要...")
    result = client.summary(session_id)
    print(f"   原始Token数: {result['tokens_before']:,}")
    print(f"   摘要Token数: {result['tokens_after']:,}")
    print(f"\n   摘要内容:")
    print(f"   {result['summary'][:200]}...")
    
    # 清理
    client.delete_session(session_id)
    print()


def example_memory_search():
    """记忆搜索示例"""
    print("=" * 70)
    print("示例 4: 记忆搜索")
    print("=" * 70)
    
    client = ReMeClient()
    
    session_id = "search_session"
    client.create_session(session_id)
    
    # 添加多轮对话
    print(f"\n添加对话内容...")
    conversations = [
        ("Python的优势是什么？", "Python语法简洁，学习曲线平缓，拥有丰富的第三方库。"),
        ("如何安装Python库？", "使用pip install命令可以安装Python库。"),
        ("什么是虚拟环境？", "虚拟环境可以为不同项目创建独立的Python环境。"),
        ("推荐的IDE有哪些？", "PyCharm、VSCode、Jupyter Notebook都是很好的选择。"),
    ]
    
    for user_msg, assistant_msg in conversations:
        messages = [
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg * 5},  # 扩展内容
        ]
        client.add_messages(session_id, messages)
    
    # 搜索记忆
    print(f"\n搜索记忆...")
    query = "如何安装库"
    result = client.search(session_id, query, max_results=3)
    
    print(f"   查询: '{query}'")
    print(f"   找到 {result['result_count']} 个相关结果:")
    for i, item in enumerate(result['results'][:3], 1):
        content = str(item.get('content', item))
        print(f"     [{i}] {content[:100]}...")
    
    # 清理
    client.delete_session(session_id)
    print()


def example_multi_session():
    """多会话管理示例"""
    print("=" * 70)
    print("示例 5: 多会话管理")
    print("=" * 70)
    
    client = ReMeClient()
    
    # 创建多个会话
    print(f"\n创建3个会话...")
    session_ids = ["session_001", "session_002", "session_003"]
    for sid in session_ids:
        client.create_session(sid)
        # 添加一些消息
        messages = [
            {"role": "user", "content": f"这是 {sid} 的消息"},
            {"role": "assistant", "content": f"收到来自 {sid} 的消息"},
        ]
        client.add_messages(sid, messages)
    
    # 列出所有会话
    print(f"\n列出所有会话...")
    result = client.list_sessions()
    print(f"   会话数量: {result['count']}")
    print(f"   会话列表: {result['sessions']}")
    
    # 查看全局统计
    print()
    client.print_global_stats()
    
    # 清理所有会话
    print(f"\n清理所有会话...")
    for sid in session_ids:
        client.delete_session(sid)
    print(f"   已删除 {len(session_ids)} 个会话")
    print()


def example_tool_result_compression():
    """Tool结果压缩示例"""
    print("=" * 70)
    print("示例 6: Tool结果压缩")
    print("=" * 70)
    
    client = ReMeClient()
    
    session_id = "tool_session"
    client.create_session(session_id)
    
    # 模拟工具调用和大量结果
    print(f"\n添加包含Tool结果的消息...")
    import json
    
    messages = [
        {"role": "user", "content": "搜索Python教程"},
        {
            "role": "assistant",
            "content": None,
            "metadata": {
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "web_search", "arguments": '{"query": "Python tutorials"}'},
                }]
            },
        },
        {
            "role": "tool",
            "content": json.dumps({
                "results": [
                    {"title": f"Python Tutorial {i}", "snippet": f"Learn Python programming..." * 20}
                    for i in range(100)  # 大量搜索结果
                ]
            }),
            "metadata": {"tool_call_id": "call_1"},
        },
        {"role": "user", "content": "总结一下主要内容"},
    ]
    client.add_messages(session_id, messages)
    
    # 压缩Tool结果
    print(f"\n压缩Tool结果...")
    result = client.compact(session_id, compact_type="tool_result")
    print(f"   Tool结果压缩:")
    print(f"     原始: {result['tokens_before']:,} tokens")
    print(f"     压缩后: {result['tokens_after']:,} tokens")
    print(f"     节省: {result['tokens_saved']:,} tokens ({result['compression_ratio']:.1%})")
    
    # 清理
    client.delete_session(session_id)
    print()


def main():
    """运行所有示例"""
    try:
        print("\n" + "=" * 70)
        print("ReMe压缩服务示例程序")
        print("=" * 70 + "\n")
        
        example_basic_workflow()
        time.sleep(1)
        
        example_long_conversation()
        time.sleep(1)
        
        example_summary_generation()
        time.sleep(1)
        
        example_memory_search()
        time.sleep(1)
        
        example_multi_session()
        time.sleep(1)
        
        example_tool_result_compression()
        
        print("=" * 70)
        print("✅ 所有示例运行完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保服务器正在运行：")
        print("  python -m compress_reme.reme_server")


if __name__ == "__main__":
    main()
