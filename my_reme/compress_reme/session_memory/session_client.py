"""
Session Memory Client - 极简客户端

使用示例:
    from session_client import SessionClient
    
    client = SessionClient(base_url="http://localhost:8789")
    
    # 获取上下文
    context = client.get(session_id="session_001", query="散热")
    
    # 添加消息
    client.add(
        session_id="session_001",
        messages=[
            {"role": "user", "content": "问题"},
            {"role": "assistant", "content": "回答"}
        ]
    )
"""

import requests
from typing import List, Dict, Any, Optional


class SessionClient:
    """Session Memory 极简客户端 - 只提供 add 和 get 两个方法"""
    
    def __init__(self, base_url: str):
        """
        初始化客户端
        
        Args:
            base_url: API服务地址（如 http://localhost:8789）
        """
        self.base_url = base_url.rstrip('/')
    
    def get(
        self, 
        session_id: str, 
        query: str = "",
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        获取session上下文
        
        Args:
            session_id: 会话ID
            query: 查询内容（用于检索相关对话）
            top_k: 返回相关对话数量
        
        Returns:
            {
                "session_id": "session_001",
                "context": "对话摘要: ...\n\n近期对话:\n...",
                "state": "产品信息: MD500, 故障码: E001",
                "summary": "...",
                "messages": [...]
            }
        """
        try:
            response = requests.post(
                f"{self.base_url}/get_message",
                json={
                    "session_id": session_id,
                    "query": query,
                    "top_k": top_k
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    return {
                        "session_id": data.get('session_id'),
                        "context": data.get('context', ''),
                        "state": data.get('state', ''),
                        "summary": data.get('summary', ''),
                        "messages": data.get('messages', [])
                    }
            
            return {"error": f"获取失败: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
    
    def add(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        fault_code: Optional[List[str]] = None,
        function_code: Optional[List[str]] = None,
        product_code: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        添加消息到session
        
        Args:
            session_id: 会话ID
            messages: 消息列表 [{"role": "user", "content": "..."}, ...]
            fault_code: 故障码列表（可选）
            function_code: 功能码列表（可选）
            product_code: 产品码列表（可选）
        
        Returns:
            {"success": True, "message_count": 2, ...}
        """
        try:
            payload = {
                "session_id": session_id,
                "messages": messages,
                "fault_code": fault_code or [],
                "function_code": function_code or [],
                "product_code": product_code or []
            }
            
            response = requests.post(
                f"{self.base_url}/add_message",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return {
                        "success": True,
                        **result.get('data', {})
                    }
            
            return {"success": False, "error": f"添加失败: {response.status_code}"}
        
        except Exception as e:
            return {"success": False, "error": f"请求异常: {str(e)}"}
