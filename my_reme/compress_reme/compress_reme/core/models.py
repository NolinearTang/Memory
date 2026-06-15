"""数据模型定义

定义API请求和响应的数据结构。
"""

from typing import Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """消息模型"""
    name: str | None = Field(None, description="消息发送者名称（如不指定则使用role）")
    role: str = Field(..., description="消息角色: user/assistant/system/tool")
    content: str | None = Field(None, description="消息内容")
    tool_calls: list[dict[str, Any]] | None = Field(None, description="工具调用")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    session_id: str = Field(..., description="会话ID")
    llm_config: dict[str, Any] | None = Field(None, description="LLM配置")
    embedding_config: dict[str, Any] | None = Field(None, description="Embedding配置")


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    session_id: str
    status: str
    message: str


class AddMessagesRequest(BaseModel):
    """添加消息请求"""
    session_id: str = Field(..., description="会话ID")
    messages: list[Message] = Field(..., description="消息列表")


class AddMessagesResponse(BaseModel):
    """添加消息响应"""
    session_id: str
    message_count: int
    total_messages: int


class CompactRequest(BaseModel):
    """压缩请求"""
    session_id: str = Field(..., description="会话ID")
    compact_type: str = Field(default="auto", description="压缩类型: auto/tool_result/memory")
    threshold: int | None = Field(None, description="压缩阈值（token数）")


class CompactResponse(BaseModel):
    """压缩响应"""
    session_id: str
    tokens_before: int
    tokens_after: int
    tokens_saved: int
    compression_ratio: float
    compact_type: str


class SummaryRequest(BaseModel):
    """摘要请求"""
    session_id: str = Field(..., description="会话ID")
    background: bool = Field(default=False, description="是否后台执行")


class SummaryResponse(BaseModel):
    """摘要响应"""
    session_id: str
    summary: str
    tokens_before: int
    tokens_after: int
    is_background: bool


class SearchRequest(BaseModel):
    """搜索请求"""
    session_id: str = Field(..., description="会话ID")
    query: str = Field(..., description="搜索查询")
    max_results: int = Field(default=5, description="最大结果数")
    min_score: float = Field(default=0.1, description="最小相关性分数")


class SearchResponse(BaseModel):
    """搜索响应"""
    session_id: str
    query: str
    results: list[dict[str, Any]]
    result_count: int


class GetMessagesRequest(BaseModel):
    """获取消息请求"""
    session_id: str = Field(..., description="会话ID")
    limit: int | None = Field(None, description="返回消息数量限制")


class GetMessagesResponse(BaseModel):
    """获取消息响应"""
    session_id: str
    messages: list[dict[str, Any]]
    total_count: int


class SessionStatsResponse(BaseModel):
    """会话统计响应"""
    session_id: str
    message_count: int
    total_tokens: int
    created_at: str
    last_active: str


class DeleteSessionResponse(BaseModel):
    """删除会话响应"""
    session_id: str
    status: str
    message: str


class GlobalStatsResponse(BaseModel):
    """全局统计响应"""
    total_sessions: int
    active_sessions: int
    total_messages: int
    total_tokens_saved: int
    uptime_seconds: float
    start_time: str
