"""FastAPI server for compress_reme.

This module provides the HTTP API server for session-based
dialogue compression and memory extraction.
"""

from .app import app, session_manager

__all__ = ["app", "session_manager"]
