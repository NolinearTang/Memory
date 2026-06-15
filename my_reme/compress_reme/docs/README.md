# ReMe 压缩服务

基于 ReMe (Retrieval-enhanced Memory) 的 Session 级别对话压缩和记忆抽取服务。

> **⚠️ 重要说明**: 
> 
> **compress_reme 是一个独立的项目**，可以单独运行和部署。
> 
> - 工作目录：应设置为 `compress_reme` 文件夹本身
> - 独立安装：可以 `pip install -e .` 安装为独立包
> - 不修改 ReMe：完全通过组合和封装实现，不修改 ReMe 源码

## 功能特性

- ✅ **Session 管理** - 多会话隔离，每个会话独立管理对话上下文
- ✅ **对话压缩** - 基于 ReMe 的智能对话压缩（Tool结果压缩、记忆压缩）
- ✅ **摘要生成** - 自动生成对话摘要，提取关键信息
- ✅ **记忆搜索** - 语义搜索对话历史和记忆
- ✅ **HTTP API** - RESTful API 接口，支持跨语言调用
- ✅ **Python 客户端** - 简洁的 Python SDK

## 系统架构

```
┌─────────────┐
│   Client    │ (Python/HTTP)
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│   FastAPI Server        │
│  (reme_server.py)       │
└──────────┬──────────────┘
           │
           ▼
    ┌──────────────┐
    │SessionManager│
    └──────┬───────┘
           │
      ┌────┴────┐
      │Sessions │
      └────┬────┘
           │
    ┌──────▼──────────┐
    │   ReMeLight     │ (每个session一个实例)
    │  - compact      │
    │  - summary      │
    │  - search       │
    └─────────────────┘
```

## 安装依赖

> **工作目录**: 所有操作在 `compress_reme` 目录下执行

### 方式 1: 安装为可编辑包（推荐）

```bash
# 进入 compress_reme 目录
cd compress_reme

# 先安装 ReMe 依赖
cd ../ReMe
pip install -e .

# 回到 compress_reme 并安装
cd ../compress_reme
pip install -e .
```

这样安装后，可以在任何目录使用：
- `compress-reme-server` - 启动服务器
- `compress-reme-client` - 运行客户端测试
- `compress-reme-example` - 运行示例

### 方式 2: 手动安装依赖

```bash
# 进入 compress_reme 目录
cd compress_reme

# 安装 ReMe
cd ../ReMe
pip install -e .

# 安装其他依赖
cd ../compress_reme
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件（参考 ReMe 的 example.env）：

```bash
# LLM API配置
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1

# Embedding API配置（可选）
EMBEDDING_API_KEY=your-api-key
EMBEDDING_BASE_URL=https://api.openai.com/v1
```

## 快速开始

> **重要**: 确保当前工作目录是 `compress_reme`

### 1. 启动服务器

```bash
# 进入 compress_reme 目录
cd compress_reme

# 方式 1: 使用便捷脚本（推荐）
./run_server.sh              # macOS/Linux
run_server.bat               # Windows

# 方式 2: 使用 Python 模块
python -m compress_reme.reme_server

# 方式 3: 如果已安装为包
compress-reme-server         # 从任何目录运行
```

服务器启动后：
- API 地址: `http://localhost:8788`
- API 文档: `http://localhost:8788/docs`
- 健康检查: `http://localhost:8788/health`

### 2. 使用 Python 客户端

```python
from compress_reme.reme_client import ReMeClient

# 创建客户端
client = ReMeClient("http://localhost:8788")

# 创建会话
client.create_session("my_session")

# 添加消息
messages = [
    {"role": "user", "content": "你好，请介绍一下Python。"},
    {"role": "assistant", "content": "Python是一种高级编程语言..."},
]
client.add_messages("my_session", messages)

# 压缩对话
result = client.compact("my_session")
print(f"节省了 {result['tokens_saved']} tokens!")

# 生成摘要
summary = client.summary("my_session")
print(f"摘要: {summary['summary']}")

# 搜索记忆
search_result = client.search("my_session", "Python的特点")
print(f"找到 {search_result['result_count']} 个结果")

# 删除会话
client.delete_session("my_session")
```

### 3. 运行示例

```bash
# 运行完整示例
python -m compress_reme.example

# 或测试客户端
python -m compress_reme.reme_client
```

## API 端点

### Session 管理

#### POST /sessions
创建新会话

**请求体**：
```json
{
  "session_id": "session_001",
  "llm_config": {
    "model_name": "gpt-4o"
  },
  "embedding_config": null
}
```

**响应**：
```json
{
  "session_id": "session_001",
  "status": "success",
  "message": "Session created successfully"
}
```

#### DELETE /sessions/{session_id}
删除会话

#### GET /sessions
列出所有会话

### 消息管理

#### POST /sessions/{session_id}/messages
添加消息到会话

**请求体**：
```json
{
  "session_id": "session_001",
  "messages": [
    {
      "role": "user",
      "content": "Hello!",
      "name": "user",
      "metadata": {}
    }
  ]
}
```

#### GET /sessions/{session_id}/messages
获取会话消息

**参数**：
- `limit` (可选): 返回消息数量限制

### 对话处理

#### POST /sessions/{session_id}/compact
压缩对话

**请求体**：
```json
{
  "session_id": "session_001",
  "compact_type": "auto",  // auto/tool_result/memory
  "threshold": 100000
}
```

**响应**：
```json
{
  "session_id": "session_001",
  "tokens_before": 50000,
  "tokens_after": 10000,
  "tokens_saved": 40000,
  "compression_ratio": 0.8,
  "compact_type": "auto"
}
```

#### POST /sessions/{session_id}/summary
生成对话摘要

**请求体**：
```json
{
  "session_id": "session_001",
  "background": false
}
```

**响应**：
```json
{
  "session_id": "session_001",
  "summary": "本次对话讨论了Python编程语言的特点...",
  "tokens_before": 50000,
  "tokens_after": 500,
  "is_background": false
}
```

#### POST /sessions/{session_id}/search
搜索记忆

**请求体**：
```json
{
  "session_id": "session_001",
  "query": "Python的特点",
  "max_results": 5,
  "min_score": 0.1
}
```

**响应**：
```json
{
  "session_id": "session_001",
  "query": "Python的特点",
  "results": [
    {"content": "...相关内容...", "score": 0.95}
  ],
  "result_count": 3
}
```

### 统计信息

#### GET /sessions/{session_id}/stats
获取会话统计

```json
{
  "session_id": "session_001",
  "message_count": 100,
  "total_tokens": 50000,
  "created_at": "2026-06-13T15:00:00",
  "last_active": "2026-06-13T16:00:00"
}
```

#### GET /stats
获取全局统计

```json
{
  "total_sessions": 5,
  "active_sessions": 5,
  "total_messages": 500,
  "total_tokens_saved": 200000,
  "uptime_seconds": 3600.5,
  "start_time": "2026-06-13T15:00:00"
}
```

#### GET /health
健康检查

## 使用场景

### 1. 长对话管理

```python
client = ReMeClient()
session_id = "long_conversation"

# 创建会话
client.create_session(session_id)

# 添加大量对话
for i in range(100):
    messages = [
        {"role": "user", "content": f"问题 {i}"},
        {"role": "assistant", "content": f"回答 {i}" * 100},
    ]
    client.add_messages(session_id, messages)

# 定期压缩以节省 tokens
result = client.compact(session_id)
print(f"压缩节省: {result['tokens_saved']} tokens")
```

### 2. 对话摘要

```python
# 对长对话生成摘要
summary = client.summary(session_id)
print(f"对话摘要: {summary['summary']}")

# 摘要可用于：
# - 快速回顾对话内容
# - 构建上下文窗口
# - 知识库构建
```

### 3. 语义搜索

```python
# 搜索历史对话中的相关内容
result = client.search(
    session_id,
    query="如何使用Python处理数据",
    max_results=5
)

for item in result['results']:
    print(f"相关内容: {item}")
```

### 4. Tool 结果压缩

```python
# 添加包含大量 Tool 结果的消息
messages = [
    {"role": "user", "content": "搜索Python教程"},
    {
        "role": "tool",
        "content": json.dumps({"results": [...]}),  # 大量搜索结果
    },
]
client.add_messages(session_id, messages)

# 压缩 Tool 结果
result = client.compact(session_id, compact_type="tool_result")
print(f"Tool结果压缩比: {result['compression_ratio']:.1%}")
```

### 5. 多会话管理

```python
# 为不同用户/任务创建独立会话
user_sessions = {}

for user_id in ["user_001", "user_002", "user_003"]:
    session_id = f"session_{user_id}"
    client.create_session(session_id)
    user_sessions[user_id] = session_id

# 每个会话独立管理对话
client.add_messages(user_sessions["user_001"], messages_1)
client.add_messages(user_sessions["user_002"], messages_2)

# 查看所有会话
sessions = client.list_sessions()
print(f"活跃会话: {sessions['sessions']}")
```

## 高级配置

### 自定义 LLM 配置

```python
# 创建会话时指定 LLM 配置
client.create_session(
    session_id="custom_session",
    llm_config={
        "model_name": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 4000,
    }
)
```

### 服务器配置

```bash
# 自定义端口
python -m compress_reme.reme_server --port 8800

# 开发模式（自动重载）
python -m compress_reme.reme_server --reload

# 自定义日志级别
python -m compress_reme.reme_server --log-level debug
```

## 性能优化

- **Session 隔离** - 每个 session 独立的 ReMeLight 实例，避免干扰
- **自动清理** - 支持清理不活跃的 session，释放资源
- **异步处理** - 基于 FastAPI 的异步架构，高并发性能
- **增量压缩** - 支持对新增消息进行增量压缩

## 与 ReMe 的关系

本服务是 **ReMe 的封装层**，提供：

1. **Session 管理** - ReMe 本身不提供多会话管理
2. **HTTP API** - 使 ReMe 可以通过 HTTP 调用
3. **简化接口** - 封装 ReMe 的复杂配置，提供简洁 API
4. **扩展功能** - 添加会话统计、批量操作等功能

**不修改 ReMe 源码**，完全通过组合和封装实现。

## 故障排除

### 无法连接服务器

```bash
# 检查服务器是否运行
curl http://localhost:8788/health

# 检查端口是否被占用
lsof -i :8788
```

### ReMe 未安装

```bash
# 安装 ReMe
cd ../ReMe
pip install -e .
```

### LLM API 配置问题

检查 `.env` 文件或环境变量：
```bash
echo $LLM_API_KEY
echo $LLM_BASE_URL
```

## 许可证

MIT License

## 相关链接

- [ReMe GitHub](https://github.com/modelscope/agentscope)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [AgentScope 文档](https://modelscope.github.io/agentscope/)
