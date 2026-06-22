# 带Session的聊天功能说明

## 🎯 功能概述

现在 `/chat` API 已完全集成 Session Memory 功能：
1. **自动获取上下文** - 根据 session_id 自动获取历史对话
2. **自动保存对话** - 每次对话自动保存到 session
3. **前端自动管理** - 前端自动生成和传递 session_id

## 🚀 使用方式

### 方式1: 前端使用（推荐）

```bash
# 1. 启动服务
python -m __main__

# 2. 打开浏览器
http://localhost:8789/chat-ui

# 前端会自动：
# - 生成 session_id（存储在 localStorage）
# - 每次发送消息时传递 session_id
# - 后端自动获取上下文并保存对话
```

**前端特性：**
- ✅ 页面标题显示当前模型名称
- ✅ 显示会话ID
- ✅ 自动保存所有对话
- ✅ 自动使用历史上下文

### 方式2: API调用

```python
import requests

session_id = "my_session_001"

# 第一次对话
response1 = requests.post(
    "http://localhost:8789/chat",
    json={
        "message": "MD500变频器显示E001报警",
        "session_id": session_id
    }
)
print(response1.json()['reply'])
# 对话自动保存到 session

# 第二次对话（会自动获取上下文）
response2 = requests.post(
    "http://localhost:8789/chat",
    json={
        "message": "如何解决这个问题？",
        "session_id": session_id  # 使用相同的session_id
    }
)
print(response2.json()['reply'])
# AI能看到之前的对话上下文
```

## 📊 工作流程

```
用户发送消息
    ↓
前端传递: {message, session_id}
    ↓
后端 /chat API
    ↓
1. 根据session_id获取历史上下文
    ↓
2. 构造输入：上下文 + 当前问题
    ↓
3. 调用 LLM 生成回复
    ↓
4. 保存 [用户消息 + AI回复] 到 session
    ↓
返回回复给前端
```

## 🔍 查看保存的Session

### 方法1: API查看

```bash
# 列出所有session
curl http://localhost:8789/sessions

# 查看特定session的内容
curl -X POST http://localhost:8789/get_message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_001",
    "query": ""
  }'
```

### 方法2: 查看存储文件

```bash
# Session数据保存在这里
ls -la .session_memory/messages/
ls -la .session_memory/metadata/

# 查看具体session的数据
cat .session_memory/messages/my_session_001.json
```

## 📝 Session数据结构

保存的数据包括：

```json
{
  "session_id": "my_session_001",
  "messages": [
    {
      "role": "user",
      "content": "MD500变频器显示E001报警",
      "timestamp": "2026-06-22T20:00:00"
    },
    {
      "role": "assistant",
      "content": "E001是过热保护报警...",
      "timestamp": "2026-06-22T20:00:05"
    }
  ],
  "summary": "讨论了MD500变频器E001报警问题...",
  "fault_code": ["E001"],
  "product_code": ["MD500"]
}
```

## 🎯 上下文获取策略

后端自动执行：

1. **检索相关对话** - 使用 BM25 检索与当前问题最相关的历史对话
2. **获取会话摘要** - 获取整个会话的摘要
3. **构造上下文** - 组合摘要和相关对话
4. **传递给LLM** - LLM基于上下文生成回复

## 🔧 后端日志

启动后可以看到详细日志：

```
[session_xxx] 收到聊天请求: MD500变频器...
[session_xxx] 获取到上下文，长度: 256
[session_xxx] LLM回复: E001是过热保护报警...
[session_xxx] 对话已保存
```

## 💡 使用场景

### 场景1: 技术支持对话

```python
session_id = "support_001"

# 第1轮
chat("变频器报警E001", session_id)
# AI: "E001是过热保护..."

# 第2轮（AI能记住之前讨论的是E001）
chat("如何散热？", session_id)
# AI: "针对E001过热问题，建议..."

# 第3轮（AI能记住整个故障排查过程）
chat("还有其他方法吗？", session_id)
# AI: "除了刚才提到的散热方法..."
```

### 场景2: 多轮问答

```python
session_id = "qa_001"

chat("什么是变频器？", session_id)
chat("它的工作原理是什么？", session_id)  # AI知道"它"指变频器
chat("有哪些应用场景？", session_id)      # AI知道问的是变频器的应用
```

## 🎨 前端界面

页面显示：
```
💬 LLM 对话测试 (qwen3.6-35b-a3b)
会话ID: session_1234567890_abc...

┌─────────────────────────────┐
│  你好！我是AI助手...         │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 用户: MD500报警E001         │  ←
└─────────────────────────────┘

┌─────────────────────────────┐
│ 助手: E001是过热保护...     │
└─────────────────────────────┘

[输入框] [发送]
```

## 🔄 Session管理

### 查看所有Session

```bash
curl http://localhost:8789/sessions

# 响应
{
  "sessions": [
    "session_1234567890_abc",
    "my_session_001",
    "support_001"
  ]
}
```

### 清除Session（前端）

```javascript
// 清除当前session_id，下次刷新会生成新的
localStorage.removeItem('chat_session_id');
location.reload();
```

## ⚙️ 配置

### 修改上下文检索数量

编辑 `app.py`:

```python
# 获取更多上下文
context_data = await manager.get_messages(
    session_id=session_id, 
    query=request.message, 
    top_k=5  # 默认3，可以改为5或更多
)
```

### 自定义System Prompt

编辑 `app.py`:

```python
# 针对技术支持的prompt
system_prompt = """你是一个工控设备技术支持专家。
请基于提供的上下文信息，准确回答用户关于变频器、PLC等设备的问题。"""
```

## 📊 性能说明

- **上下文获取**: ~50ms
- **LLM调用**: 2-10秒（取决于模型）
- **保存对话**: ~20ms
- **总响应时间**: 主要取决于LLM

## 🔍 调试

### 查看后端日志

```bash
# 启动时查看日志
python -m __main__

# 看到以下日志表示正常
[session_xxx] 收到聊天请求: ...
[session_xxx] 获取到上下文，长度: ...
[session_xxx] LLM回复: ...
[session_xxx] 对话已保存
```

### 查看前端日志

```javascript
// 浏览器控制台（F12）
当前会话ID: session_xxx
当前配置: {selected_model: "qwen", ...}
```

### 验证保存

```bash
# 查看session文件
ls -lh .session_memory/messages/

# 查看内容
cat .session_memory/messages/session_xxx.json | jq
```

## 🎯 总结

现在的聊天功能：

✅ **自动上下文** - 无需手动传递，后端自动获取  
✅ **自动保存** - 每次对话自动保存到session  
✅ **前端集成** - session_id自动生成和传递  
✅ **完整日志** - 详细的操作日志  
✅ **灵活配置** - 可以自定义各种参数  

只需：
1. 启动服务
2. 打开浏览器
3. 开始对话

所有的上下文管理和保存都是自动的！🎉
