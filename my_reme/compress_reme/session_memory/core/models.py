from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="user或assistant")
    content: str = Field(..., description="消息内容")


class AddMessageRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID，不传时默认用 session_id")
    messages: List[Message] = Field(..., description="当前轮次的对话信息")
    fault_code: List[Any] = Field(default_factory=list, description="故障码列表")
    function_code: List[Any] = Field(default_factory=list, description="功能码列表")
    product_code: List[Any] = Field(default_factory=list, description="产品信息列表")


class AddMessageResponse(BaseModel):
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应信息")
    data: Dict[str, Any] = Field(default_factory=dict, description="响应数据")


class GetMessageRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID，不传时默认用 session_id")
    query: str = Field(..., description="查询内容，用于检索相关对话")


class GetMessageResponse(BaseModel):
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应信息")
    data: Dict[str, Any] = Field(..., description="响应数据")


class SessionData(BaseModel):
    session_id: str
    fault_code: List[Any] = Field(default_factory=list)
    function_code: List[Any] = Field(default_factory=list)
    product_code: List[Any] = Field(default_factory=list)
    session_summary: str = ""
    facts: List[str] = Field(default_factory=list)  # 对话中的客观事实，用户澄清优先
    all_messages: List[Dict[str, str]] = Field(default_factory=list)
    recent_messages: List[Dict[str, Any]] = Field(default_factory=list)  # 允许Any类型（支持original_length为int）
    message_summaries: Dict[int, str] = Field(default_factory=dict)  # 消息压缩缓存
    last_summarized_index: int = 0  # 上次summary处理到的消息索引
    last_facts_index: int = 0       # 上次facts处理到的消息索引（实时更新，无缓冲）
