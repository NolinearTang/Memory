"""Session管理器

管理多个ReMeLight实例，每个session对应一个独立的对话上下文。
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any
import logging

from agentscope.message import Msg

try:
    from reme.reme_light import ReMeLight
except ImportError:
    raise ImportError(
        "请先安装 reme 包:\n"
        "  pip install reme\n"
        "或者从源码安装:\n"
        "  cd <ReMe目录> && pip install -e ."
    )

logger = logging.getLogger(__name__)


def get_default_llm_config() -> dict[str, Any]:
    """从环境变量获取默认LLM配置"""
    config = {}
    
    if os.getenv("LLM_MODEL_NAME"):
        config["model_name"] = os.getenv("LLM_MODEL_NAME")
    
    if os.getenv("LLM_API_KEY"):
        config["api_key"] = os.getenv("LLM_API_KEY")
    
    if os.getenv("LLM_BASE_URL"):
        config["base_url"] = os.getenv("LLM_BASE_URL")
    
    return config


def get_default_embedding_config() -> dict[str, Any]:
    """从环境变量获取默认Embedding配置"""
    config = {}
    
    if os.getenv("EMBEDDING_MODEL_NAME"):
        config["model_name"] = os.getenv("EMBEDDING_MODEL_NAME")
    
    if os.getenv("EMBEDDING_API_KEY"):
        config["api_key"] = os.getenv("EMBEDDING_API_KEY")
    
    if os.getenv("EMBEDDING_BASE_URL"):
        config["base_url"] = os.getenv("EMBEDDING_BASE_URL")
    
    return config


class SessionInfo:
    """Session信息类"""
    
    def __init__(self, session_id: str, reme_instance: ReMeLight):
        self.session_id = session_id
        self.reme = reme_instance
        self.messages: list[Msg] = []
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.total_tokens = 0
        self.tokens_saved = 0
    
    def update_active(self):
        """更新最后活跃时间"""
        self.last_active = datetime.now()
    
    def add_messages(self, messages: list[Msg]):
        """添加消息"""
        self.messages.extend(messages)
        self.update_active()
    
    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "total_tokens": self.total_tokens,
            "tokens_saved": self.tokens_saved,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
        }


class SessionManager:
    """Session管理器
    
    管理多个session的生命周期，每个session对应一个ReMeLight实例。
    """
    
    def __init__(
        self,
        working_dir: str = ".reme_sessions",
        default_llm_config: dict | None = None,
        default_embedding_config: dict | None = None,
    ):
        """初始化Session管理器
        
        Args:
            working_dir: 工作目录，每个session在此目录下创建子目录
            default_llm_config: 默认LLM配置（如果为None，从环境变量读取）
            default_embedding_config: 默认Embedding配置（如果为None，从环境变量读取）
        """
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用提供的配置，或从环境变量读取
        if default_llm_config is None:
            default_llm_config = get_default_llm_config()
        if default_embedding_config is None:
            default_embedding_config = get_default_embedding_config()
        
        self.default_llm_config = default_llm_config
        self.default_embedding_config = default_embedding_config
        
        self.sessions: dict[str, SessionInfo] = {}
        self.start_time = datetime.now()
        
        logger.info(f"SessionManager initialized at {self.working_dir}")
        if self.default_llm_config:
            logger.info(f"Default LLM config: model={self.default_llm_config.get('model_name', 'not set')}")
    
    async def create_session(
        self,
        session_id: str,
        llm_config: dict | None = None,
        embedding_config: dict | None = None,
    ) -> SessionInfo:
        """创建新session
        
        Args:
            session_id: 会话ID
            llm_config: LLM配置（可选）
            embedding_config: Embedding配置（可选）
            
        Returns:
            SessionInfo实例
            
        Raises:
            ValueError: 如果session_id已存在
        """
        if session_id in self.sessions:
            raise ValueError(f"Session {session_id} already exists")
        
        # 创建session工作目录
        session_dir = self.working_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 合并配置
        final_llm_config = {**self.default_llm_config, **(llm_config or {})}
        final_embedding_config = {**self.default_embedding_config, **(embedding_config or {})}
        
        # 创建ReMeLight实例
        reme = ReMeLight(
            working_dir=str(session_dir),
            default_as_llm_config=final_llm_config,
            default_embedding_model_config=final_embedding_config,
            enable_load_env=True,
        )
        
        # 启动ReMeLight
        await reme.start()
        
        # 创建SessionInfo
        session_info = SessionInfo(session_id, reme)
        self.sessions[session_id] = session_info
        
        logger.info(f"Created session: {session_id}")
        return session_info
    
    def get_session(self, session_id: str) -> SessionInfo:
        """获取session
        
        Args:
            session_id: 会话ID
            
        Returns:
            SessionInfo实例
            
        Raises:
            KeyError: 如果session不存在
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        return self.sessions[session_id]
    
    async def delete_session(self, session_id: str) -> bool:
        """删除session
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功删除
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # 关闭ReMeLight实例
        try:
            await session.reme.close()
        except Exception as e:
            logger.warning(f"Error closing session {session_id}: {e}")
        
        # 删除session
        del self.sessions[session_id]
        
        logger.info(f"Deleted session: {session_id}")
        return True
    
    def list_sessions(self) -> list[str]:
        """列出所有session ID"""
        return list(self.sessions.keys())
    
    def get_global_stats(self) -> dict[str, Any]:
        """获取全局统计信息"""
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        total_tokens_saved = sum(s.tokens_saved for s in self.sessions.values())
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(self.sessions),
            "total_messages": total_messages,
            "total_tokens_saved": total_tokens_saved,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat(),
        }
    
    async def cleanup_inactive_sessions(self, max_inactive_seconds: int = 3600):
        """清理不活跃的session
        
        Args:
            max_inactive_seconds: 最大不活跃时间（秒）
        """
        now = datetime.now()
        to_delete = []
        
        for session_id, session in self.sessions.items():
            inactive_seconds = (now - session.last_active).total_seconds()
            if inactive_seconds > max_inactive_seconds:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            await self.delete_session(session_id)
            logger.info(f"Cleaned up inactive session: {session_id}")
        
        return len(to_delete)
    
    async def shutdown(self):
        """关闭所有session"""
        logger.info("Shutting down SessionManager...")
        
        for session_id in list(self.sessions.keys()):
            await self.delete_session(session_id)
        
        logger.info("SessionManager shut down")
