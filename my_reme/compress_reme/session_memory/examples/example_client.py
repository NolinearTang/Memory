import requests
import time
import json


BASE_URL = "http://localhost:8789"


def add_message(session_id, messages, fault_code=None, function_code=None, product_code=None):
    url = f"{BASE_URL}/add_message"
    data = {
        "session_id": session_id,
        "messages": messages,
        "fault_code": fault_code or [],
        "function_code": function_code or [],
        "product_code": product_code or [],
    }
    
    response = requests.post(url, json=data)
    return response.json()


def get_message(session_id, query):
    url = f"{BASE_URL}/get_message"
    data = {
        "session_id": session_id,
        "query": query,
    }
    
    response = requests.post(url, json=data)
    return response.json()


def list_sessions():
    url = f"{BASE_URL}/sessions"
    response = requests.get(url)
    return response.json()


def main():
    print("=" * 60)
    print("Session Memory API 客户端示例")
    print("=" * 60)
    
    session_id = "demo_session_001"
    
    print(f"\n1. 添加第一轮对话")
    result1 = add_message(
        session_id=session_id,
        messages=[
            {"role": "user", "content": "变频器显示E001错误，怎么处理？"},
            {"role": "assistant", "content": "E001是过热保护报警。请检查：1）环境温度是否过高 2）负载是否过大 3）散热风扇是否正常 4）温度传感器是否异常。建议先降低负载运行，观察是否还会报警。"},
        ],
        fault_code=["E001"],
        function_code=["F100"],
        product_code=["MD500"],
    )
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    time.sleep(1)
    
    print(f"\n2. 添加第二轮对话")
    result2 = add_message(
        session_id=session_id,
        messages=[
            {"role": "user", "content": "降低负载后还是报警"},
            {"role": "assistant", "content": "如果降低负载后仍然报警，建议：1）检查散热风扇是否损坏 2）清理变频器内部灰尘 3）检查环境通风是否良好 4）使用万用表测量温度传感器阻值是否正常 5）检查变频器参数设置是否合理。如果以上都正常，可能是温度传感器故障，需要更换。"},
        ],
        fault_code=["E001"],
        product_code=["MD500"],
    )
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    time.sleep(1)
    
    print(f"\n3. 添加第三轮对话")
    result3 = add_message(
        session_id=session_id,
        messages=[
            {"role": "user", "content": "散热风扇转速很慢"},
            {"role": "assistant", "content": "散热风扇转速慢是导致过热的主要原因。请：1）检查风扇电源电压是否正常（通常为24V DC）2）检查风扇轴承是否卡滞 3）清理风扇叶片上的灰尘 4）如果风扇老化，建议直接更换新风扇。更换后记得测试风扇转速，确保达到额定转速。"},
        ],
        fault_code=["E001"],
        product_code=["MD500"],
    )
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    print("\n等待后台处理（3秒）...")
    time.sleep(3)
    
    print(f"\n4. 获取对话上下文（查询：风扇）")
    context1 = get_message(session_id, "风扇问题")
    print(f"\n状态: {context1['data']['state']}")
    print(f"\n上下文:\n{context1['data']['context']}")
    
    print(f"\n5. 获取对话上下文（查询：传感器）")
    context2 = get_message(session_id, "温度传感器")
    print(f"\n上下文:\n{context2['data']['context']}")
    
    print(f"\n6. 列出所有会话")
    sessions = list_sessions()
    print(json.dumps(sessions, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
    print("\n提示：")
    print("- 可以继续添加更多对话，系统会自动进行摘要和压缩")
    print("- 超过3轮的旧对话会被提取摘要")
    print("- 长回答（>200字）会被自动压缩")
    print("- BM25检索可以找到相关的历史对话")


if __name__ == "__main__":
    main()
