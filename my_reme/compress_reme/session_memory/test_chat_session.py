"""
测试chat API的session功能
"""
import asyncio
import requests
import json


def test_chat_with_session():
    """测试带session的聊天"""
    base_url = "http://localhost:8789"
    session_id = "test_session_001"
    
    print("=" * 60)
    print("测试 /chat API 的 Session 功能")
    print("=" * 60)
    
    # 第一轮对话
    print("\n第1轮对话:")
    response1 = requests.post(
        f"{base_url}/chat",
        json={
            "message": "MD500变频器显示E001报警",
            "session_id": session_id
        }
    )
    
    if response1.ok:
        data1 = response1.json()
        print(f"用户: MD500变频器显示E001报警")
        print(f"AI: {data1['reply'][:100]}...")
        print("✅ 对话1成功，已保存到session")
    else:
        print(f"❌ 失败: {response1.status_code} - {response1.text}")
        return
    
    # 第二轮对话（测试上下文）
    print("\n第2轮对话（测试上下文获取）:")
    response2 = requests.post(
        f"{base_url}/chat",
        json={
            "message": "如何解决这个问题？",
            "session_id": session_id
        }
    )
    
    if response2.ok:
        data2 = response2.json()
        print(f"用户: 如何解决这个问题？")
        print(f"AI: {data2['reply'][:100]}...")
        print("✅ 对话2成功，AI应该能理解'这个问题'指E001报警")
    else:
        print(f"❌ 失败: {response2.status_code} - {response2.text}")
        return
    
    # 第三轮对话
    print("\n第3轮对话:")
    response3 = requests.post(
        f"{base_url}/chat",
        json={
            "message": "还有其他建议吗？",
            "session_id": session_id
        }
    )
    
    if response3.ok:
        data3 = response3.json()
        print(f"用户: 还有其他建议吗？")
        print(f"AI: {data3['reply'][:100]}...")
        print("✅ 对话3成功")
    else:
        print(f"❌ 失败: {response3.status_code} - {response3.text}")
        return
    
    # 查看session内容
    print("\n查看保存的session内容:")
    response_get = requests.post(
        f"{base_url}/get_message",
        json={
            "session_id": session_id,
            "query": ""
        }
    )
    
    if response_get.ok:
        session_data = response_get.json()
        print(f"Session ID: {session_data.get('session_id')}")
        print(f"消息数量: {len(session_data.get('messages', []))}")
        print(f"摘要: {session_data.get('summary', '无')[:100]}...")
        print("✅ Session数据保存成功")
    else:
        print(f"❌ 获取session失败: {response_get.status_code}")
    
    # 查看所有sessions
    print("\n查看所有sessions:")
    response_sessions = requests.get(f"{base_url}/sessions")
    if response_sessions.ok:
        sessions = response_sessions.json()
        print(f"所有sessions: {sessions}")
        if session_id in sessions.get('sessions', []):
            print(f"✅ 找到测试session: {session_id}")
        else:
            print(f"⚠️  未找到测试session")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


def test_chat_without_session():
    """测试不带session的聊天（默认session）"""
    base_url = "http://localhost:8789"
    
    print("\n" + "=" * 60)
    print("测试不带 session_id 的对话（使用默认session）")
    print("=" * 60)
    
    response = requests.post(
        f"{base_url}/chat",
        json={"message": "你好"}
    )
    
    if response.ok:
        data = response.json()
        print(f"用户: 你好")
        print(f"AI: {data['reply'][:100]}...")
        print("✅ 默认session对话成功")
    else:
        print(f"❌ 失败: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("请确保服务已启动: python -m __main__\n")
    
    try:
        # 测试服务是否运行
        response = requests.get("http://localhost:8789/health")
        if not response.ok:
            print("❌ 服务未运行，请先启动: python -m __main__")
            exit(1)
        
        print("✅ 服务运行中\n")
        
        # 运行测试
        test_chat_with_session()
        test_chat_without_session()
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务")
        print("请先启动服务: python -m __main__")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
