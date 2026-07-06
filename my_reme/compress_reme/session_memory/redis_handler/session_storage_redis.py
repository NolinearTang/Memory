import json
import logging
from typing import Dict, List, Optional

from core.models import SessionData
from redis_handler.redis_client import RedisClient

logger = logging.getLogger(__name__)

# 默认 TTL
DEFAULT_SINGLE_TURN_TTL = 7 * 24 * 3600   # 7天
DEFAULT_MULTI_TURN_TTL  = 30 * 24 * 3600  # 30天

# Redis Key 规范
#
#   sm:user:{user_id}:session:{session_id}:meta  → SessionData JSON，带 TTL
#   sm:user:{user_id}:session:{session_id}:msgs  → 消息列表 JSON，带 TTL
#   sm:sid:{session_id}                          → user_id，反向索引，同 TTL
#
# sm:sid 用于仅有 session_id 时快速定位路径，内存缓存作为加速层（重启后从 Redis 恢复）。


class RedisSessionStorage:
    """
    基于 Redis 的 session 存储，接口与 SessionStorage 保持一致。

    Key 结构：
      sm:user:{user_id}:session:{session_id}:meta  → JSON(SessionData)，带 TTL
      sm:user:{user_id}:session:{session_id}:msgs  → JSON(List[msg])，带 TTL

    TTL 规则：
      单轮对话（≤2条消息）→ single_turn_ttl（默认7天）
      多轮对话（>2条消息）→ multi_turn_ttl（默认30天）

    反向索引 sm:sid:{session_id} 持久化到 Redis，与 meta 同 TTL，服务重启后仍可用。
    内存缓存 _sid_to_uid 作为加速层，命中时跳过 Redis 读取。
    """

    def __init__(
        self,
        redis_client: RedisClient,
        single_turn_ttl: int = DEFAULT_SINGLE_TURN_TTL,
        multi_turn_ttl: int = DEFAULT_MULTI_TURN_TTL,
    ):
        self.r = redis_client
        self.single_turn_ttl = single_turn_ttl
        self.multi_turn_ttl  = multi_turn_ttl
        # 内存缓存：session_id → user_id，避免重复 SCAN
        self._sid_to_uid: Dict[str, str] = {}

    # ---------- 内部 key helpers ----------

    def _meta_key(self, user_id: str, session_id: str) -> str:
        return f"sm:user:{user_id}:session:{session_id}:meta"

    def _msgs_key(self, user_id: str, session_id: str) -> str:
        return f"sm:user:{user_id}:session:{session_id}:msgs"

    def _ttl(self, msg_count: int) -> int:
        return self.single_turn_ttl if msg_count <= 2 else self.multi_turn_ttl

    def _sid_key(self, session_id: str) -> str:
        return f"sm:sid:{session_id}"

    def _resolve_user_id(self, session_id: str) -> Optional[str]:
        """
        获取 session_id 对应的 user_id。
        优先查内存缓存，缓存未命中则查 Redis 反向索引 sm:sid:{session_id}。
        """
        if session_id in self._sid_to_uid:
            return self._sid_to_uid[session_id]
        # 从 Redis 反向索引读取
        raw = self.r.client.get(self._sid_key(session_id))
        if not raw:
            return None
        user_id = raw.decode() if isinstance(raw, bytes) else raw
        self._sid_to_uid[session_id] = user_id  # 写入内存缓存
        return user_id

    # ---------- 用户-会话纳管 ----------

    def register_user_session(self, user_id: str, session_id: str):
        """写内存缓存 + Redis 反向索引（TTL 在 save_metadata 时统一刷新）"""
        self._sid_to_uid[session_id] = user_id
        self.r.client.set(self._sid_key(session_id), user_id)  # 暂不设 TTL，save_metadata 时统一刷新

    def list_sessions_by_user(self, user_id: str) -> List[str]:
        """返回 user_id 下所有存活的 session_id"""
        pattern = f"sm:user:{user_id}:session:*:meta"
        keys = self.r.client.keys(pattern)
        result = []
        for k in keys:
            k_str = k.decode() if isinstance(k, bytes) else k
            # 格式: sm:user:{user_id}:session:{session_id}:meta
            parts = k_str.split(":")
            if len(parts) == 6:
                result.append(parts[4])
        return result

    # ---------- 消息存储 ----------

    def append_messages(self, session_id: str, messages: List[Dict]):
        user_id = self._sid_to_uid.get(session_id, session_id)
        key = self._msgs_key(user_id, session_id)
        raw = self.r.client.get(key)
        existing = json.loads(raw) if raw else []
        existing.extend(messages)
        self.r.client.set(key, json.dumps(existing, ensure_ascii=False))
        # TTL 在 save_metadata 时统一刷新

    def read_all_messages(self, session_id: str) -> List[Dict]:
        user_id = self._resolve_user_id(session_id) or session_id
        raw = self.r.client.get(self._msgs_key(user_id, session_id))
        return json.loads(raw) if raw else []

    # ---------- 元数据存储 ----------

    def save_metadata(self, session_id: str, data: SessionData):
        user_id = self._sid_to_uid.get(session_id) or self._resolve_user_id(session_id) or session_id
        ttl = self._ttl(len(data.all_messages))
        meta_json = json.dumps(data.model_dump(), ensure_ascii=False)
        self.r.client.set(self._meta_key(user_id, session_id), meta_json, ex=ttl)
        self.r.client.expire(self._msgs_key(user_id, session_id), ttl)
        # 反向索引与 meta 同 TTL，确保 meta 过期时 sid 索引也一起过期
        self.r.client.set(self._sid_key(session_id), user_id, ex=ttl)
        logger.debug(f"[Redis] save user={user_id} session={session_id} TTL={ttl}s ({len(data.all_messages)} msgs)")

    def load_metadata(self, session_id: str) -> Optional[SessionData]:
        user_id = self._resolve_user_id(session_id) or session_id
        raw = self.r.client.get(self._meta_key(user_id, session_id))
        if not raw:
            return None
        try:
            return SessionData(**json.loads(raw))
        except Exception as e:
            logger.error(f"[Redis] load_metadata {session_id} 解析失败: {e}")
            return None

    def session_exists(self, session_id: str) -> bool:
        user_id = self._resolve_user_id(session_id) or session_id
        return self.r.client.exists(self._meta_key(user_id, session_id)) > 0

    def list_sessions(self) -> List[str]:
        """列出所有 session"""
        keys = self.r.client.keys("sm:user:*:session:*:meta")
        result = []
        for k in keys:
            k_str = k.decode() if isinstance(k, bytes) else k
            parts = k_str.split(":")
            if len(parts) == 6:
                result.append(parts[4])
        return result
