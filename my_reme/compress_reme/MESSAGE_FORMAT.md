# Message 格式说明

## 你只需要传什么

### 最简单的格式（推荐）

```python
from compress_reme import ReMeClient

client = ReMeClient("http://localhost:8788")

# ✅ 只传 role 和 content，最简单！
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "system", "content": "You are a helpful assistant."},
]

client.add_messages("session_001", messages)
```

**说明**：
- `role`：必填，可以是 `user`、`assistant`、`system`、`tool`
- `content`：消息内容（可选）
- `name`：不需要传，会自动使用 `role` 的值

## 数据转换流程

### 1️⃣ 你传入的 JSON

```json
{
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there"}
  ]
}
```

### 2️⃣ FastAPI + Pydantic 自动解析

```python
# Pydantic 根据 Message 模型自动转换
class Message(BaseModel):
    name: str | None = None          # 你没传，自动填充为 None
    role: str                         # "user" 或 "assistant"
    content: str | None = None        # "Hello" 或 "Hi there"
    tool_calls: list | None = None    # 你没传，自动填充为 None
    metadata: dict = {}               # 你没传，自动填充为 {}
```

### 3️⃣ 服务端转换为 AgentScope Msg

```python
# 服务端代码
msgs = [
    Msg(
        name=msg.name or msg.role,  # None or "user" → "user"
        role=msg.role,               # "user"
        content=msg.content,         # "Hello"
        **msg.metadata,              # {}
    )
    for msg in request.messages
]
```

**结果**：
```python
Msg(name="user", role="user", content="Hello")
Msg(name="assistant", role="assistant", content="Hi there")
```

## 完整格式（可选字段）

如果你需要更精细的控制，可以传完整格式：

```python
messages = [
    {
        "name": "Alice",              # 可选：自定义发送者名称
        "role": "user",               # 必填：角色
        "content": "Hello!",          # 可选：消息内容
        "tool_calls": [...],          # 可选：工具调用
        "metadata": {                 # 可选：元数据
            "timestamp": "2024-01-01",
            "user_id": "123",
        }
    },
    {
        "name": "Bob",
        "role": "assistant",
        "content": "Hi there!"
    }
]
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `role` | str | ✅ 是 | - | 消息角色：user/assistant/system/tool |
| `content` | str | ❌ 否 | None | 消息内容 |
| `name` | str | ❌ 否 | None | 发送者名称，不传则使用 role |
| `tool_calls` | list | ❌ 否 | None | 工具调用（用于 function calling） |
| `metadata` | dict | ❌ 否 | {} | 自定义元数据 |

## 实际使用示例

### 示例 1：简单对话

```python
client.add_messages("session_001", [
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "It's sunny today!"},
])
```

**转换后**：
```python
Msg(name="user", role="user", content="What's the weather?")
Msg(name="assistant", role="assistant", content="It's sunny today!")
```

### 示例 2：多用户对话（指定 name）

```python
client.add_messages("session_001", [
    {"name": "Alice", "role": "user", "content": "Hello everyone!"},
    {"name": "Bob", "role": "user", "content": "Hi Alice!"},
    {"name": "assistant", "role": "assistant", "content": "Hello Alice and Bob!"},
])
```

**转换后**：
```python
Msg(name="Alice", role="user", content="Hello everyone!")
Msg(name="Bob", role="user", content="Hi Alice!")
Msg(name="assistant", role="assistant", content="Hello Alice and Bob!")
```

### 示例 3：带元数据

```python
client.add_messages("session_001", [
    {
        "role": "user",
        "content": "Book a flight",
        "metadata": {
            "timestamp": "2024-01-01 10:00:00",
            "user_id": "user_123",
            "session_type": "booking"
        }
    }
])
```

### 示例 4：Tool Calls（function calling）

```python
client.add_messages("session_001", [
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "Beijing"}'
                }
            }
        ]
    },
    {
        "role": "tool",
        "name": "get_weather",
        "content": '{"temperature": 20, "condition": "sunny"}'
    }
])
```

## 常见问题

### Q: 为什么要区分 `name` 和 `role`？

**A**: 
- `role` 是系统级别的角色标识（user/assistant/system/tool）
- `name` 是具体的身份标识（如 "Alice"、"Bob"、"GPT-4"）

在简单场景下，它们可以相同。在多用户或多助手场景下，`name` 用于区分不同的人。

### Q: 我可以只传 `{"content": "Hello"}` 吗？

**A**: 不可以。`role` 是必填字段。最少要传：
```python
{"role": "user", "content": "Hello"}
```

### Q: `content` 可以为空吗？

**A**: 可以。例如在 function calling 场景下，只有 `tool_calls` 没有 `content`：
```python
{"role": "assistant", "tool_calls": [...]}
```

### Q: 如果我传了 `name`，会发生什么？

**A**: 会使用你传的 `name`：
```python
# 输入
{"name": "GPT-4", "role": "assistant", "content": "Hello"}

# 输出
Msg(name="GPT-4", role="assistant", content="Hello")
```

### Q: 如果我不传 `name`，会发生什么？

**A**: 会自动使用 `role` 作为 `name`：
```python
# 输入
{"role": "assistant", "content": "Hello"}

# 输出
Msg(name="assistant", role="assistant", content="Hello")
```

## 总结

**最简单的用法**（覆盖 90% 的场景）：
```python
messages = [
    {"role": "user", "content": "你的问题"},
    {"role": "assistant", "content": "AI的回答"}
]
```

就这么简单！ 🎉
