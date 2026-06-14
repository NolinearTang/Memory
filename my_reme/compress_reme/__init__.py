"""ReMe压缩服务包

基于Session的对话压缩和记忆抽取服务。
"""

from .reme_client import ReMeClient
from .session_manager import SessionManager, SessionInfo

__all__ = ["ReMeClient", "SessionManager", "SessionInfo"]
__version__ = "1.0.0"
