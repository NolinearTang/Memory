"""
Session Memory - 基于对话摘要和BM25检索的会话记忆系统
"""

from core.session_manager import SessionMemoryManager
from core.models import Message, AddMessageRequest, GetMessageRequest, AddMessageResponse, GetMessageResponse
from core.summarizer import ConversationSummarizer
from core.storage import SessionStorage
from retrieval.bm25_retriever import BM25Retriever
from config import get_config, Config

__version__ = "1.1.0"

__all__ = [
    "SessionMemoryManager",
    "Message",
    "AddMessageRequest",
    "GetMessageRequest", 
    "AddMessageResponse",
    "GetMessageResponse",
    "ConversationSummarizer",
    "SessionStorage",
    "BM25Retriever",
    "get_config",
    "Config",
]
