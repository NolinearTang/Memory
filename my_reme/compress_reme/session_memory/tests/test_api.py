import asyncio
import time
from core.session_manager import SessionMemoryManager
from core.models import Message


async def test_session_memory():
    print("=" * 60)
    print("Session Memory 测试")
    print("=" * 60)
    
    manager = SessionMemoryManager(storage_dir=".test_session_memory")
    
    session_id = "test_session_001"
    
    print(f"\n1. 添加第一轮对话到会话 {session_id}")
    result1 = await manager.add_message(
        session_id=session_id,
        messages=[
            Message(role="user", content="请问MD500变频器出现E001故障码是什么原因？"),
            Message(role="assistant", content="E001故障码通常表示电机过热保护。可能的原因包括：1. 环境温度过高 2. 电机负载过大 3. 散热系统故障 4. 温度传感器异常。建议先检查电机温度是否正常，然后检查散热风扇是否正常工作。"),
        ],
        fault_code=["E001"],
        function_code=["F100"],
        product_code=["MD500"],
    )
    print(f"结果: {result1}")
    
    await asyncio.sleep(2)
    
    print(f"\n2. 添加第二轮对话")
    result2 = await manager.add_message(
        session_id=session_id,
        messages=[
            Message(role="user", content="散热风扇正常，但是电机温度还是很高，怎么办？"),
            Message(role="assistant", content="如果散热风扇正常但电机温度仍然很高，建议：1. 检查电机负载是否超出额定值 2. 检查环境通风是否良好 3. 检查电机内部是否有异物堵塞 4. 检查变频器输出参数是否合理 5. 考虑增加外部散热措施。如果问题持续，建议联系专业技术人员进行现场检查。"),
        ],
        fault_code=["E001"],
        function_code=["F100"],
        product_code=["MD500"],
    )
    print(f"结果: {result2}")
    
    await asyncio.sleep(2)
    
    print(f"\n3. 添加第三轮对话")
    result3 = await manager.add_message(
        session_id=session_id,
        messages=[
            Message(role="user", content="已经检查了负载，负载是正常的。"),
            Message(role="assistant", content="负载正常的情况下，建议进一步检查：1. 变频器的输出频率和电压是否匹配电机额定参数 2. 检查电机轴承是否磨损导致摩擦增大 3. 检查定子绕组绝缘是否老化 4. 使用红外测温仪测量电机各部位温度分布，找出热点。"),
        ],
        fault_code=["E001"],
        function_code=["F100"],
        product_code=["MD500"],
    )
    print(f"结果: {result3}")
    
    await asyncio.sleep(2)
    
    print(f"\n4. 添加第四轮对话（触发摘要生成）")
    result4 = await manager.add_message(
        session_id=session_id,
        messages=[
            Message(role="user", content="用红外测温发现电机底部温度特别高。"),
            Message(role="assistant", content="电机底部温度特别高很可能是轴承问题。建议：1. 立即停机检查 2. 拆卸电机检查下轴承 3. 检查轴承是否缺油、磨损或损坏 4. 如轴承损坏需及时更换 5. 重新安装时确保轴承安装正确、润滑充足。轴承问题如不及时处理可能导致更严重的设备损坏。"),
        ],
        fault_code=["E001"],
        function_code=["F100"],
        product_code=["MD500"],
    )
    print(f"结果: {result4}")
    
    print("\n等待后台处理完成...")
    await asyncio.sleep(5)
    
    print(f"\n5. 获取对话上下文（查询：轴承）")
    context_result = await manager.get_message(
        session_id=session_id,
        query="轴承问题",
        top_k=3,
    )
    print(f"\n响应码: {context_result['code']}")
    print(f"消息: {context_result['message']}")
    print(f"\n状态信息:")
    print(context_result['data']['state'])
    print(f"\n上下文信息:")
    print(context_result['data']['context'])
    
    print(f"\n6. 获取对话上下文（查询：散热）")
    context_result2 = await manager.get_message(
        session_id=session_id,
        query="散热问题",
        top_k=3,
    )
    print(f"\n上下文信息:")
    print(context_result2['data']['context'])
    
    print(f"\n7. 列出所有会话")
    sessions = manager.list_sessions()
    print(f"会话列表: {sessions}")
    
    await manager.shutdown()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_session_memory())
