"""Core components for compress_reme.

This module contains the core data models and session management logic.
"""

from .models import (
    Message,
    CreateSessionRequest,
    CreateSessionResponse,
    DeleteSessionResponse,
    AddMessagesRequest,
    AddMessagesResponse,
    GetMessagesResponse,
    CompactRequest,
    CompactResponse,
    SummaryRequest,
    SummaryResponse,
    SearchRequest,
    SearchResponse,
    SessionStatsResponse,
    GlobalStatsResponse,
)
from .session_manager import SessionManager, SessionInfo

__all__ = [
    # Models
    "Message",
    "CreateSessionRequest",
    "CreateSessionResponse",
    "DeleteSessionResponse",
    "AddMessagesRequest",
    "AddMessagesResponse",
    "GetMessagesResponse",
    "CompactRequest",
    "CompactResponse",
    "SummaryRequest",
    "SummaryResponse",
    "SearchRequest",
    "SearchResponse",
    "SessionStatsResponse",
    "GlobalStatsResponse",
    # Session Management
    "SessionManager",
    "SessionInfo",
]
