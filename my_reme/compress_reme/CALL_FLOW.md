# 调用逻辑说明

## 完整的调用链路

```
┌─────────────┐        HTTP         ┌─────────────┐        Python      ┌─────────────┐
│   你的代码   │  ────────────────>  │   客户端     │  ────────────────> │   服务端     │
│  (使用方)   │   requests.post    │ ReMeClient  │   FastAPI路由     │   app.py    │
└─────────────┘                     └─────────────┘                    └─────────────┘
```

## 1️⃣ 客户端调用逻辑

### 位置：`compress_reme/client/client.py`

```python
# 第 102-130 行：add_messages 方法
def add_messages(self, session_id: str, messages: list[dict[str, Any]]):
    """添加消息到会话"""
    
    # 1. 构造 URL
    url = f"{self.base_url}/sessions/{session_id}/messages"
    #     ↓
    # http://localhost:8788/sessions/session_001/messages
    
    # 2. 构造请求体
    payload = {
        "session_id": session_id,
        "messages": messages,  # 你传入的消息列表
    }
    
    # 3. 发送 HTTP POST 请求
    response = requests.post(url, json=payload, timeout=self.timeout)
    #                             ↑
    #                   自动转为 JSON 格式
    
    # 4. 检查响应
    response.raise_for_status()  # 如果失败会抛异常
    
    # 5. 返回 JSON 响应
    return response.json()
```

## 2️⃣ 服务端接收逻辑

### 位置：`compress_reme/server/app.py`

```python
# 第 208-237 行：add_messages 接口
@app.post("/sessions/{session_id}/messages", response_model=AddMessagesResponse)
async def add_messages(session_id: str, request: AddMessagesRequest):
    """
    FastAPI 路由处理函数
    
    参数：
    - session_id: 从 URL 路径中提取 (/sessions/{session_id}/messages)
    - request: FastAPI 自动将 JSON body 解析为 AddMessagesRequest 对象
    """
    
    # 1. 获取或创建 session (第 212 行)
    session = await get_or_create_session(session_id)
    #         ↓
    #   如果 session 不存在，自动创建
    
    # 2. 转换消息格式 (第 215-224 行)
    msgs = [
        Msg(
            name=msg.name or msg.role,  # 如果 name 为 None，用 role
            role=msg.role,
            content=msg.content,
            **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
            **msg.metadata,
        )
        for msg in request.messages  # request.messages 已被解析为 Message 对象列表
    ]
    
    # 3. 添加到 session (第 226 行)
    session.add_messages(msgs)
    
    # 4. 返回响应 (第 229-233 行)
    return AddMessagesResponse(
        session_id=session_id,
        message_count=len(msgs),
        total_messages=len(session.messages),
    )
```

## 3️⃣ 完整调用示例

### 示例 1：最简单的用法

```python
from compress_reme.client import ReMeClient

# 创建客户端
client = ReMeClient("http://localhost:8788")

# 准备消息
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there"}
]

# 调用
result = client.add_messages("session_001", messages)
print(result)
# 输出: {'session_id': 'session_001', 'message_count': 2, 'total_messages': 2}
```

**数据流转**：

```python
# 你的代码
messages = [{"role": "user", "content": "Hello"}]
      ↓
# 客户端 (client.py line 127)
requests.post(url, json={"session_id": "session_001", "messages": messages})
      ↓
# HTTP 请求
POST /sessions/session_001/messages
Body: {"session_id": "session_001", "messages": [{"role": "user", "content": "Hello"}]}
      ↓
# FastAPI 自动解析 (Pydantic)
request = AddMessagesRequest(
    session_id="session_001",
    messages=[Message(name=None, role="user", content="Hello", metadata={})]
)
      ↓
# 服务端处理 (app.py line 217)
msg = Msg(name="user", role="user", content="Hello")
      ↓
# 添加到 session
session.add_messages([msg])
      ↓
# 返回响应
{"session_id": "session_001", "message_count": 1, "total_messages": 1}
```

### 示例 2：压缩调用

```python
# 1. 添加消息
client.add_messages("session_001", messages)

# 2. 压缩对话
result = client.compact("session_001")
```

**调用链路**：

```python
# 客户端 (client.py line 154-185)
def compact(self, session_id: str, compact_type: str = "auto"):
    url = f"{self.base_url}/sessions/{session_id}/compact"
    payload = {"session_id": session_id, "compact_type": compact_type, ...}
    response = requests.post(url, json=payload)
    return response.json()
      ↓
# 服务端 (app.py line 276-325)
@app.post("/sessions/{session_id}/compact")
async def compact_conversation(session_id: str, request: CompactRequest):
    session = await get_or_create_session(session_id)
    reme = session.reme
    
    # 执行压缩
    session.messages = await reme.compact_tool_result(session.messages)
    # 或
    compact_result = await reme.compact_memory(messages=session.messages)
    
    return CompactResponse(...)
```

## 4️⃣ 实际运行示例

### 启动服务器

```bash
# 终端 1：启动服务器
cd /Users/tangshisong/.../compress_reme
python -m compress_reme.server.app

# 输出：
# INFO: ReMe服务器启动成功
# INFO: Uvicorn running on http://0.0.0.0:8788
```

### 调用客户端

```bash
# 终端 2：运行客户端测试
python -m compress_reme.client.client

# 或者写自己的脚本
```

**你自己的脚本示例**：

```python
# my_script.py
from compress_reme.client import ReMeClient

client = ReMeClient("http://localhost:8788")

# 添加消息（自动创建 session）
messages = [
    {"role": "user", "content": "介绍Python"},
    {"role": "assistant", "content": "Python是..." * 100}  # 很长的回复
]
client.add_messages("my_session", messages)

# 压缩
result = client.compact("my_session")
print(f"节省了 {result['tokens_saved']} tokens!")

# 生成摘要
summary = client.summary("my_session")
print(f"摘要: {summary['summary']}")
```

## 5️⃣ 关键代码位置速查

| 功能 | 客户端位置 | 服务端位置 |
|------|-----------|-----------|
| 创建会话 | `client.py:46-73` | `app.py:125-148` |
| 添加消息 | `client.py:102-130` | `app.py:208-237` |
| 压缩对话 | `client.py:154-185` | `app.py:276-325` |
| 生成摘要 | `client.py:187-214` | `app.py:328-366` |
| 搜索记忆 | `client.py:216-246` | `app.py:369-404` |
| 获取消息 | `client.py:132-152` | `app.py:240-269` |
| 自动创建 | - | `app.py:183-204` |

## 6️⃣ 测试示例

### 客户端内置测试

```bash
# 运行内置测试（client.py line 316-377）
python -m compress_reme.client.client
```

测试流程：
1. 创建会话
2. 添加消息
3. 压缩对话
4. 生成摘要
5. 查看统计
6. 删除会话

### 配置示例

```bash
# 查看配置示例
python examples/config_example.py
```

位置：`examples/config_example.py:9-97`

## 7️⃣ HTTP 请求格式

### 添加消息

```http
POST /sessions/session_001/messages HTTP/1.1
Host: localhost:8788
Content-Type: application/json

{
  "session_id": "session_001",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi there"
    }
  ]
}
```

**响应**：

```json
{
  "session_id": "session_001",
  "message_count": 2,
  "total_messages": 2
}
```

### 压缩对话

```http
POST /sessions/session_001/compact HTTP/1.1
Host: localhost:8788
Content-Type: application/json

{
  "session_id": "session_001",
  "compact_type": "auto",
  "threshold": null
}
```

**响应**：

```json
{
  "session_id": "session_001",
  "tokens_before": 1500,
  "tokens_after": 800,
  "tokens_saved": 700,
  "compression_ratio": 0.467,
  "compact_type": "auto"
}
```

## 8️⃣ 错误处理

### 客户端错误处理

```python
try:
    result = client.add_messages("session_001", messages)
except requests.exceptions.ConnectionError:
    print("服务器未启动")
except requests.exceptions.HTTPError as e:
    print(f"HTTP错误: {e.response.status_code}")
    print(f"详情: {e.response.json()}")
```

### 服务端错误处理

```python
# app.py 中的异常处理
try:
    session = await get_or_create_session(session_id)
    # ... 处理逻辑
except Exception as e:
    logger.error(f"添加消息失败: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
```

## 总结

**调用链路**：
```
你的代码 
  → ReMeClient.add_messages() 
    → requests.post() 
      → FastAPI路由 @app.post() 
        → get_or_create_session() 
          → 转换消息 
            → session.add_messages() 
              → 返回响应
```

**关键文件**：
1. **客户端**：`compress_reme/client/client.py`
2. **服务端**：`compress_reme/server/app.py`
3. **模型**：`compress_reme/core/models.py`
4. **示例**：`examples/config_example.py`
5. **测试**：`client.py` 的 `main()` 函数
