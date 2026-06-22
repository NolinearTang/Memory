#!/usr/bin/env python3
"""
Session数据调试工具 - 查看get_message返回的数据和送给LLM的数据
"""
import requests
import json
import sys


def debug_session(session_id: str, query: str = ""):
    """调试指定session的数据"""
    base_url = "http://localhost:8789"
    
    print("=" * 80)
    print(f"📊 Session数据调试")
    print(f"Session ID: {session_id}")
    print(f"Query: {query or '(空)'}")
    print("=" * 80)
    
    try:
        # 调用调试端点
        response = requests.post(
            f"{base_url}/debug/context",
            json={
                "session_id": session_id,
                "query": query
            }
        )
        
        if not response.ok:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        
        # 1. 显示基本信息
        print("\n📋 基本信息:")
        print(f"  Session ID: {data.get('session_id')}")
        print(f"  Query: {data.get('query')}")
        print(f"  是否有上下文: {'✅ 是' if data.get('will_use_context') else '❌ 否'}")
        print(f"  上下文长度: {data.get('context_length')} 字符")
        
        # 2. 显示get_message的完整返回
        print("\n" + "=" * 80)
        print("📦 get_message() 返回的数据:")
        print("=" * 80)
        
        result = data.get('get_message_result', {})
        print(f"\nCode: {result.get('code')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('code') == 200:
            result_data = result.get('data', {})
            
            # State信息
            state = result_data.get('state', '')
            if state:
                print(f"\n📌 State信息:")
                print(f"  {state}")
            
            # Context信息
            context = result_data.get('context', '')
            if context:
                print(f"\n📝 Context信息:")
                print("-" * 80)
                print(context)
                print("-" * 80)
            else:
                print(f"\n⚠️  没有历史上下文（可能是首次对话）")
        else:
            print(f"\n❌ 获取数据失败: {result.get('message')}")
        
        # 3. 显示会送给LLM的数据
        print("\n" + "=" * 80)
        print("🤖 送给LLM的数据:")
        print("=" * 80)
        
        llm_input = data.get('llm_input', {})
        
        print(f"\n模型: {llm_input.get('model')}")
        print(f"用户输入长度: {llm_input.get('user_input_length')} 字符")
        
        print(f"\n--- System Prompt ---")
        print(llm_input.get('system_prompt', ''))
        
        print(f"\n--- User Input ---")
        user_input = llm_input.get('user_input', '')
        if len(user_input) > 500:
            print(user_input[:500] + f"\n... (共 {len(user_input)} 字符，已截断)")
        else:
            print(user_input)
        
        print("\n" + "=" * 80)
        print("✅ 调试完成")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保服务已启动:")
        print("   python -m __main__")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def list_sessions():
    """列出所有session"""
    base_url = "http://localhost:8789"
    
    try:
        response = requests.get(f"{base_url}/sessions")
        if response.ok:
            sessions = response.json().get('sessions', [])
            print("\n📋 所有Session:")
            for i, sid in enumerate(sessions, 1):
                print(f"  {i}. {sid}")
            return sessions
        else:
            print(f"❌ 获取session列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def view_session_file(session_id: str):
    """查看session的元数据文件"""
    import os
    
    metadata_file = f".session_memory/metadata/{session_id}.json"
    
    if not os.path.exists(metadata_file):
        print(f"❌ 文件不存在: {metadata_file}")
        return
    
    print(f"\n📄 Session元数据文件: {metadata_file}")
    print("=" * 80)
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(json.dumps(data, ensure_ascii=False, indent=2))


def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 80)
    print("🔍 Session数据调试工具 - 交互模式")
    print("=" * 80)
    
    # 列出所有session
    sessions = list_sessions()
    
    if not sessions:
        print("\n⚠️  没有找到任何session，请先进行对话")
        return
    
    # 选择session
    print("\n请选择要调试的session（输入序号）:")
    try:
        choice = int(input("序号: "))
        if 1 <= choice <= len(sessions):
            session_id = sessions[choice - 1]
        else:
            print("❌ 无效的序号")
            return
    except ValueError:
        print("❌ 请输入数字")
        return
    
    # 输入query
    print(f"\n选中Session: {session_id}")
    query = input("输入查询内容（直接回车跳过）: ").strip()
    
    # 调试
    debug_session(session_id, query)
    
    # 询问是否查看文件
    view_file = input("\n是否查看元数据文件？(y/n): ").strip().lower()
    if view_file == 'y':
        view_session_file(session_id)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Session Memory 数据调试工具                         ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if len(sys.argv) > 1:
        # 命令行模式
        session_id = sys.argv[1]
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        debug_session(session_id, query)
        
        # 提示查看文件
        print(f"\n💡 提示: 查看完整元数据文件:")
        print(f"   cat .session_memory/metadata/{session_id}.json | jq")
    else:
        # 交互模式
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\n👋 退出")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n使用方法:")
    print("  1. 交互模式: python debug_session.py")
    print("  2. 命令行模式: python debug_session.py <session_id> [query]")
    print("  3. 查看文件: cat .session_memory/metadata/<session_id>.json | jq")
    print()
