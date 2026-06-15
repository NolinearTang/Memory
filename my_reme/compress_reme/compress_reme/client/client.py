"""ReMe压缩服务客户端

提供简洁的API调用ReMe压缩服务。

使用示例：
    from compress_reme.reme_client import ReMeClient

    client = ReMeClient("http://localhost:8788")
    
    # 创建会话
    client.create_session("session_001")
    
    # 添加消息
    messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    client.add_messages("session_001", messages)
    
    # 压缩对话
    result = client.compact("session_001")
    print(f"节省了 {result['tokens_saved']} tokens!")
    
    # 生成摘要
    summary = client.summary("session_001")
    print(f"摘要: {summary['summary']}")
"""

import requests
from typing import Any


class ReMeClient:
    """ReMe压缩服务客户端"""

    def __init__(self, base_url: str = "http://localhost:8788", timeout: int = 120):
        """初始化客户端
        
        Args:
            base_url: 服务器地址
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def create_session(
        self,
        session_id: str,
        llm_config: dict | None = None,
        embedding_config: dict | None = None,
    ) -> dict[str, Any]:
        """创建新会话
        
        Args:
            session_id: 会话ID
            llm_config: LLM配置（可选）
            embedding_config: Embedding配置（可选）
            
        Returns:
            创建结果
        """
        url = f"{self.base_url}/sessions"
        
        payload = {
            "session_id": session_id,
            "llm_config": llm_config,
            "embedding_config": embedding_config,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def delete_session(self, session_id: str) -> dict[str, Any]:
        """删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除结果
        """
        url = f"{self.base_url}/sessions/{session_id}"
        response = requests.delete(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def list_sessions(self) -> dict[str, Any]:
        """列出所有会话
        
        Returns:
            会话列表
        """
        url = f"{self.base_url}/sessions"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def add_messages(
        self,
        session_id: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """添加消息到会话
        
        Args:
            session_id: 会话ID
            messages: 消息列表，每个消息包含:
                - role: 角色 (user/assistant/system/tool)
                - content: 内容
                - name: 发送者名称（可选）
                - metadata: 元数据（可选）
                
        Returns:
            添加结果
        """
        url = f"{self.base_url}/sessions/{session_id}/messages"
        
        payload = {
            "session_id": session_id,
            "messages": messages,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def get_messages(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """获取会话消息
        
        Args:
            session_id: 会话ID
            limit: 返回消息数量限制（可选）
            
        Returns:
            消息列表
        """
        url = f"{self.base_url}/sessions/{session_id}/messages"
        params = {"limit": limit} if limit is not None else {}
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def compact(
        self,
        session_id: str,
        compact_type: str = "auto",
        threshold: int | None = None,
    ) -> dict[str, Any]:
        """压缩对话
        
        Args:
            session_id: 会话ID
            compact_type: 压缩类型 (auto/tool_result/memory)
            threshold: 压缩阈值（token数）
            
        Returns:
            压缩结果，包含:
            - tokens_before: 压缩前token数
            - tokens_after: 压缩后token数
            - tokens_saved: 节省的token数
            - compression_ratio: 压缩比
        """
        url = f"{self.base_url}/sessions/{session_id}/compact"
        
        payload = {
            "session_id": session_id,
            "compact_type": compact_type,
            "threshold": threshold,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def summary(
        self,
        session_id: str,
        background: bool = False,
    ) -> dict[str, Any]:
        """生成对话摘要
        
        Args:
            session_id: 会话ID
            background: 是否后台执行
            
        Returns:
            摘要结果，包含:
            - summary: 摘要文本
            - tokens_before: 摘要前token数
            - tokens_after: 摘要后token数
        """
        url = f"{self.base_url}/sessions/{session_id}/summary"
        
        payload = {
            "session_id": session_id,
            "background": background,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def search(
        self,
        session_id: str,
        query: str,
        max_results: int = 5,
        min_score: float = 0.1,
    ) -> dict[str, Any]:
        """搜索记忆
        
        Args:
            session_id: 会话ID
            query: 搜索查询
            max_results: 最大结果数
            min_score: 最小相关性分数
            
        Returns:
            搜索结果
        """
        url = f"{self.base_url}/sessions/{session_id}/search"
        
        payload = {
            "session_id": session_id,
            "query": query,
            "max_results": max_results,
            "min_score": min_score,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def get_session_stats(self, session_id: str) -> dict[str, Any]:
        """获取会话统计
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话统计信息
        """
        url = f"{self.base_url}/sessions/{session_id}/stats"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def get_global_stats(self) -> dict[str, Any]:
        """获取全局统计
        
        Returns:
            全局统计信息
        """
        url = f"{self.base_url}/stats"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def health_check(self) -> dict[str, Any]:
        """健康检查
        
        Returns:
            健康状态信息
        """
        url = f"{self.base_url}/health"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def print_session_stats(self, session_id: str):
        """打印格式化的会话统计"""
        stats = self.get_session_stats(session_id)
        
        print("=" * 60)
        print(f"会话统计: {session_id}")
        print("=" * 60)
        print(f"消息数量:        {stats['message_count']:,}")
        print(f"总Token数:       {stats['total_tokens']:,}")
        print(f"创建时间:        {stats['created_at']}")
        print(f"最后活跃:        {stats['last_active']}")
        print("=" * 60)

    def print_global_stats(self):
        """打印格式化的全局统计"""
        stats = self.get_global_stats()
        
        print("=" * 60)
        print("ReMe服务全局统计")
        print("=" * 60)
        print(f"总会话数:        {stats['total_sessions']:,}")
        print(f"活跃会话数:      {stats['active_sessions']:,}")
        print(f"总消息数:        {stats['total_messages']:,}")
        print(f"总节省Tokens:    {stats['total_tokens_saved']:,}")
        print(f"运行时长:        {stats['uptime_seconds']:.2f} 秒")
        print(f"启动时间:        {stats['start_time']}")
        print("=" * 60)


def main():
    """命令行测试客户端"""
    client = ReMeClient()
    
    print("测试ReMe压缩客户端...")
    
    try:
        # 创建会话
        session_id = "test_session_001"
        print(f"\n创建会话: {session_id}")
        result = client.create_session(session_id)
        print(f"  状态: {result['status']}")
        
        # 添加消息
        print(f"\n添加消息...")
        messages = [
            {"role": "user", "content": "你好，请介绍一下Python编程语言。"},
            {"role": "assistant", "content": "Python是一种高级、解释型编程语言，以其简洁易读的语法著称。" * 50},
            {"role": "user", "content": "有哪些常用的Python库？"},
            {"role": "assistant", "content": "常用的Python库包括NumPy、Pandas、TensorFlow、Django、Flask等。" * 30},
        ]
        result = client.add_messages(session_id, messages)
        print(f"  添加消息数: {result['message_count']}")
        print(f"  总消息数: {result['total_messages']}")
        
        # 压缩对话
        print(f"\n压缩对话...")
        result = client.compact(session_id)
        print(f"  压缩前: {result['tokens_before']:,} tokens")
        print(f"  压缩后: {result['tokens_after']:,} tokens")
        print(f"  节省: {result['tokens_saved']:,} tokens ({result['compression_ratio']:.1%})")
        
        # 生成摘要
        print(f"\n生成摘要...")
        result = client.summary(session_id)
        print(f"  摘要长度: {len(result['summary'])} 字符")
        print(f"  摘要预览: {result['summary'][:100]}...")
        
        # 查看统计
        print()
        client.print_session_stats(session_id)
        
        print()
        client.print_global_stats()
        
        # 删除会话
        print(f"\n删除会话: {session_id}")
        result = client.delete_session(session_id)
        print(f"  状态: {result['status']}")
        
        print("\n✅ 所有测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动服务器：")
        print("   python -m compress_reme.reme_server")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
