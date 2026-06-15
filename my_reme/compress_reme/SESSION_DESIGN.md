# Session 设计说明

## ✅ 改进后的设计

### 核心理念

**Session 自动创建** - 用户调用任何接口时，如果 session 不存在，会自动创建，无需预先调用 `create_session()`。

### 使用方式

#### 方式一：直接使用（推荐）

```python
from compress_reme import ReMeClient

client = ReMeClient("http://localhost:8788")

# ✅ 直接使用，自动创建 session
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
]

# 添加消息（自动创建 session）
client.add_messages("session_001", messages)

# 压缩对话（自动使用已创建的 session）
result = client.compact("session_001")
print(f"节省了 {result['tokens_saved']} tokens!")

# 生成摘要
summary = client.summary("session_001")
print(f"摘要: {summary['summary']}")
```

#### 方式二：显式创建（可选）

如果你需要自定义 LLM 配置，可以显式创建 session：

```python
from compress_reme import ReMeClient

client = ReMeClient("http://localhost:8788")

# 可选：显式创建，指定配置
client.create_session(
    "session_001",
    llm_config={
        "model": "gpt-4",
        "api_key": "your-key",
    }
)

# 后续操作
client.add_messages("session_001", messages)
client.compact("session_001")
```

## 技术实现

### 服务端

添加了 `get_or_create_session()` 辅助函数：

```python
async def get_or_create_session(
    session_id: str, 
    llm_config: dict | None = None, 
    embedding_config: dict | None = None
):
    """获取或自动创建会话"""
    try:
        return session_manager.get_session(session_id)
    except KeyError:
        # Session不存在，自动创建
        logger.info(f"会话 {session_id} 不存在，自动创建")
        await session_manager.create_session(
            session_id=session_id,
            llm_config=llm_config,
            embedding_config=embedding_config,
        )
        return session_manager.get_session(session_id)
```

所有接口（add_messages, compact, summary, search, stats）都使用这个函数。

### 受影响的接口

以下接口都支持自动创建 session：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/sessions/{session_id}/messages` | POST | 添加消息 |
| `/sessions/{session_id}/messages` | GET | 获取消息 |
| `/sessions/{session_id}/compact` | POST | 压缩对话 |
| `/sessions/{session_id}/summary` | POST | 生成摘要 |
| `/sessions/{session_id}/search` | POST | 搜索记忆 |
| `/sessions/{session_id}/stats` | GET | 会话统计 |

## 优势对比

### ❌ 旧设计

```python
# 步骤1：必须先创建
client.create_session("session_001")

# 步骤2：才能使用
client.add_messages("session_001", messages)
client.compact("session_001")
```

**问题**：
- 强制两步操作
- 容易忘记创建
- 额外的网络请求
- 404 错误风险

### ✅ 新设计

```python
# 一步完成，自动创建
client.add_messages("session_001", messages)
client.compact("session_001")
```

**优势**：
- 简单直观
- 按需创建
- 减少网络请求
- 避免 404 错误

## Session 生命周期

```
第一次调用任何接口 → 自动创建 Session
    ↓
持续使用（add_messages, compact, summary等）
    ↓
调用 delete_session() → 删除 Session
    ↓
再次调用任何接口 → 重新自动创建
```

## 配置说明

### 默认配置

自动创建的 session 使用环境变量中的配置（`.env` 文件）：

```bash
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o
```

### 自定义配置

如果需要为特定 session 使用不同的配置：

```python
# 方式1：显式创建时指定
client.create_session(
    "session_001",
    llm_config={
        "model": "gpt-4-turbo",
        "api_key": "another-key",
        "base_url": "https://custom-api.com/v1"
    }
)

# 方式2：在第一次调用时传递（未实现）
# 未来可以考虑在 add_messages 等接口中接受 llm_config 参数
```

## 最佳实践

### 1. Session ID 命名

```python
# ✅ 推荐：使用有意义的 ID
session_id = f"user_{user_id}_{timestamp}"
session_id = f"conversation_{conv_id}"

# ❌ 不推荐：随机字符串
session_id = "abc123xyz"
```

### 2. Session 管理

```python
# 列出所有 session
sessions = client.list_sessions()

# 定期清理旧 session
for session_id in old_sessions:
    client.delete_session(session_id)
```

### 3. 错误处理

```python
try:
    result = client.compact("session_001", messages)
except Exception as e:
    print(f"压缩失败: {e}")
    # Session 会自动创建，错误通常来自其他原因（如 API 配置）
```

## FAQ

### Q: create_session() 还需要吗？

**A**: 可选。只有在需要自定义 LLM 配置时才需要显式调用。

### Q: 如果 session 已存在会怎样？

**A**: 直接使用现有 session，不会重复创建。

### Q: 自动创建的 session 用什么配置？

**A**: 使用环境变量或 `.env` 文件中的默认配置。

### Q: 可以修改已创建 session 的配置吗？

**A**: 目前不支持。如需修改，请先删除后重新创建：

```python
client.delete_session("session_001")
client.create_session("session_001", new_llm_config)
```

## 总结

**改进前**：必须先创建 session → 容易出错  
**改进后**：自动创建 session → 简单易用

这个设计符合"最少惊讶原则"，用户只需关注业务逻辑，无需关心 session 管理细节。
