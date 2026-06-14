"""Headroom 压缩服务客户端

提供简洁的 API 调用压缩服务。

使用示例：
    from compress.client import CompressClient

    client = CompressClient("http://localhost:8787")
    
    messages = [
        {"role": "user", "content": "Hello!"}
    ]
    
    result = client.compress(messages, model="gpt-4o")
    print(f"节省了 {result['tokens_saved']} tokens!")
    
    # 查看统计
    stats = client.get_stats()
    print(stats)
    
    # 压缩RAG内容
    rag_result = client.compress_rag(
        documents=[
            {"content": "doc content", "score": 0.9}
        ],
        query="search query"
    )
    print(rag_result)
"""

import requests
from typing import Any


class CompressClient:
    """Headroom 压缩服务客户端"""

    def __init__(self, base_url: str = "http://localhost:8787", timeout: int = 60):
        """初始化客户端
        
        Args:
            base_url: 服务器地址
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def compress(
        self,
        messages: list[dict[str, Any]],
        model: str = "gpt-4o",
        target_ratio: float | None = None,
        compress_user_messages: bool = False,
        protect_recent: int = 4,
        kompress_model: str | None = None,
    ) -> dict[str, Any]:
        """压缩消息
        
        Args:
            messages: 要压缩的消息列表
            model: 目标模型名称
            target_ratio: 目标保留率 (0-1)，None=自动决策
            compress_user_messages: 是否压缩用户消息
            protect_recent: 保护最近 N 条消息不压缩
            kompress_model: Kompress 模型ID，'disabled'=禁用ML压缩
            
        Returns:
            压缩结果字典，包含：
            - messages: 压缩后的消息
            - tokens_before: 压缩前 token 数
            - tokens_after: 压缩后 token 数
            - tokens_saved: 节省的 token 数
            - compression_ratio: 压缩比
            - transforms_applied: 应用的压缩算法
            
        Raises:
            requests.exceptions.RequestException: 请求失败
        """
        url = f"{self.base_url}/compress"
        
        payload = {
            "messages": messages,
            "model": model,
            "target_ratio": target_ratio,
            "compress_user_messages": compress_user_messages,
            "protect_recent": protect_recent,
            "kompress_model": kompress_model,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def get_stats(self) -> dict[str, Any]:
        """获取服务器统计信息
        
        Returns:
            统计信息字典
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

    def compress_rag(
        self,
        documents: list[dict[str, Any]],
        query: str,
        top_k: int | None = None,
        min_score: float = 0.0,
        target_ratio: float | None = 0.3,
        model: str = "gpt-4o",
        preserve_metadata: bool = True,
    ) -> dict[str, Any]:
        """压缩RAG检索内容
        
        Args:
            documents: 检索到的文档列表，每个文档包含:
                - content: 文档内容 (必需)
                - score: 相关性分数 0-1 (可选，默认1.0)
                - metadata: 元数据字典 (可选)
            query: 用户查询
            top_k: 保留前K个文档，None=保留所有
            min_score: 最低相关性分数阈值
            target_ratio: 每个文档的压缩保留率
            model: 目标模型
            preserve_metadata: 是否保留元数据
            
        Returns:
            RAG压缩结果字典，包含:
            - documents: 压缩后的文档列表
            - original_count: 原始文档数量
            - compressed_count: 压缩后文档数量
            - tokens_before: 压缩前token数
            - tokens_after: 压缩后token数
            - tokens_saved: 节省的token数
            - compression_ratio: 压缩比
            
        Raises:
            requests.exceptions.RequestException: 请求失败
        """
        url = f"{self.base_url}/compress-rag"
        
        payload = {
            "documents": documents,
            "query": query,
            "top_k": top_k,
            "min_score": min_score,
            "target_ratio": target_ratio,
            "model": model,
            "preserve_metadata": preserve_metadata,
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def reset_stats(self) -> dict[str, Any]:
        """重置统计信息
        
        Returns:
            操作结果
        """
        url = f"{self.base_url}/reset-stats"
        response = requests.post(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def print_stats(self):
        """打印格式化的统计信息"""
        stats = self.get_stats()
        
        print("=" * 60)
        print("Headroom 压缩服务统计")
        print("=" * 60)
        print(f"总请求数:        {stats['total_requests']:,}")
        print(f"RAG请求数:       {stats['total_rag_requests']:,}")
        print(f"总节省 tokens:   {stats['total_tokens_saved']:,}")
        print(f"压缩前 tokens:   {stats['total_tokens_before']:,}")
        print(f"压缩后 tokens:   {stats['total_tokens_after']:,}")
        print(f"平均压缩比:      {stats['average_compression_ratio']:.1%}")
        print(f"错误次数:        {stats['error_count']}")
        print(f"运行时长:        {stats['uptime_seconds']:.2f} 秒")
        print(f"启动时间:        {stats['start_time']}")
        print(f"最后请求:        {stats['last_request_time'] or 'N/A'}")
        print("=" * 60)


def main():
    """命令行测试客户端"""
    import json
    
    client = CompressClient()
    
    # 测试消息
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
                    {"title": f"Result {i}", "snippet": f"Description {i}", "score": 100 - i}
                    for i in range(500)
                ]
            }),
        },
        {"role": "user", "content": "What are the top 3 results?"},
    ]
    
    print("测试压缩客户端...")
    print(f"原始消息数: {len(messages)}")
    
    try:
        # 压缩消息
        result = client.compress(messages, model="gpt-4o")
        
        print("\n压缩结果:")
        print(f"  压缩前: {result['tokens_before']:,} tokens")
        print(f"  压缩后: {result['tokens_after']:,} tokens")
        print(f"  节省:   {result['tokens_saved']:,} tokens ({result['compression_ratio']:.1%})")
        print(f"  压缩器: {', '.join(result['transforms_applied'])}")
        
        # 打印统计
        print("\n")
        client.print_stats()
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动服务器：")
        print("   python compress_server.py")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
