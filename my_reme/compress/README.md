# Headroom 压缩服务

基于 Headroom 的消息压缩服务器和客户端。

## 功能特性

- ✅ HTTP API 压缩服务
- ✅ RAG检索内容智能压缩
- ✅ 实时统计信息
- ✅ 支持自定义压缩参数
- ✅ 简洁的 Python 客户端
- ✅ 健康检查和监控

## 安装依赖

```bash
pip install headroom-ai[all] fastapi uvicorn requests
```

## 快速开始

### 1. 启动服务器

```bash
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme
python -m compress.compress_server

# 或指定端口
python -m compress.compress_server --port 8080
```

服务器启动后：
- API 地址: `http://localhost:8787`
- API 文档: `http://localhost:8787/docs`

### 2. 使用客户端

#### 方式1：Python SDK

```python
from compress.client import CompressClient

# 创建客户端
client = CompressClient("http://localhost:8787")

# 压缩消息
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
]

result = client.compress(messages, model="gpt-4o")

print(f"压缩前: {result['tokens_before']} tokens")
print(f"压缩后: {result['tokens_after']} tokens")
print(f"节省:   {result['tokens_saved']} tokens")
print(f"压缩比: {result['compression_ratio']:.1%}")

# 使用压缩后的消息
compressed_messages = result['messages']
```

#### 方式2：直接 HTTP 请求

```python
import requests

url = "http://localhost:8787/compress"
payload = {
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "model": "gpt-4o"
}

response = requests.post(url, json=payload)
result = response.json()
```

#### 方式3：curl 命令

```bash
curl -X POST "http://localhost:8787/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "model": "gpt-4o"
  }'
```

### 3. 查看统计

```python
# 使用客户端
client.print_stats()

# 或查看原始数据
stats = client.get_stats()
print(stats)
```

```bash
# 使用 curl
curl http://localhost:8787/stats
```

### 4. 测试客户端

```bash
# 运行测试示例
python -m compress.client
```

## API 端点

### POST /compress

压缩消息。

**请求体**：
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "model": "gpt-4o",
  "target_ratio": null,
  "compress_user_messages": false,
  "protect_recent": 4,
  "kompress_model": null
}
```

**参数说明**：
- `messages` (必需): 要压缩的消息列表
- `model` (可选): 目标模型名称，默认 "gpt-4o"
- `target_ratio` (可选): 目标保留率 (0-1)，null=自动决策
- `compress_user_messages` (可选): 是否压缩用户消息，默认 false
- `protect_recent` (可选): 保护最近 N 条消息不压缩，默认 4
- `kompress_model` (可选): Kompress 模型ID，"disabled"=禁用ML压缩

**响应**：
```json
{
  "messages": [...],
  "tokens_before": 45000,
  "tokens_after": 4500,
  "tokens_saved": 40500,
  "compression_ratio": 0.9,
  "transforms_applied": ["smart_crusher", "cache_aligner"],
  "timestamp": "2026-06-12T00:45:00"
}
```

### POST /compress-rag

压缩RAG检索内容。智能过滤和压缩向量数据库检索结果。

**请求体**：
```json
{
  "documents": [
    {
      "content": "文档内容...",
      "score": 0.95,
      "metadata": {"source": "doc1.txt", "page": 1}
    }
  ],
  "query": "用户查询",
  "top_k": 5,
  "min_score": 0.5,
  "target_ratio": 0.3,
  "model": "gpt-4o",
  "preserve_metadata": true
}
```

**参数说明**：
- `documents` (必需): 检索到的文档列表，每个包含:
  - `content` (必需): 文档内容
  - `score` (可选): 相关性分数 0-1，默认 1.0
  - `metadata` (可选): 元数据字典
- `query` (必需): 用户查询
- `top_k` (可选): 保留前K个文档，null=保留所有
- `min_score` (可选): 最低相关性分数阈值，默认 0.0
- `target_ratio` (可选): 每个文档的压缩保留率，默认 0.3
- `model` (可选): 目标模型，默认 "gpt-4o"
- `preserve_metadata` (可选): 是否保留元数据，默认 true

**响应**：
```json
{
  "documents": [
    {
      "content": "压缩后的内容...",
      "score": 0.95,
      "original_length": 5000,
      "compressed_length": 1500,
      "metadata": {"source": "doc1.txt", "page": 1}
    }
  ],
  "original_count": 10,
  "compressed_count": 5,
  "tokens_before": 25000,
  "tokens_after": 5000,
  "tokens_saved": 20000,
  "compression_ratio": 0.8,
  "timestamp": "2026-06-12T01:00:00"
}
```

### GET /stats

获取统计信息。

**响应**：
```json
{
  "total_requests": 42,
  "total_tokens_before": 1000000,
  "total_tokens_after": 150000,
  "total_tokens_saved": 850000,
  "average_compression_ratio": 0.85,
  "error_count": 0,
  "uptime_seconds": 3600.5,
  "start_time": "2026-06-12T00:00:00",
  "last_request_time": "2026-06-12T00:45:00"
}
```

### GET /health

健康检查。

### POST /reset-stats

重置统计信息。

## 高级配置

### 自定义压缩参数

```python
# 保守压缩：保留 70%
result = client.compress(
    messages,
    model="gpt-4o",
    target_ratio=0.7
)

# 禁用 ML 压缩（只用规则）
result = client.compress(
    messages,
    model="gpt-4o",
    kompress_model="disabled"
)

# 压缩所有消息（包括用户消息）
result = client.compress(
    messages,
    model="gpt-4o",
    compress_user_messages=True,
    protect_recent=0
)
```

### 服务器配置

```bash
# 自定义端口
python -m compress.compress_server --port 8080

# 开发模式（自动重载）
python -m compress.compress_server --reload

# 自定义日志级别
python -m compress.compress_server --log-level debug
```

### 环境变量

```bash
# Kompress 后端选择
export HEADROOM_KOMPRESS_BACKEND=onnx_cpu

# HuggingFace 缓存路径
export HF_HOME=/your/custom/path/huggingface

# 并发限制
export HEADROOM_KOMPRESS_MAX_CONCURRENT=2
```

## 集成到现有代码

### 与 LLM API 集成

```python
from compress.client import CompressClient
import requests

client = CompressClient()

# 原始消息
messages = [...]

# 压缩
result = client.compress(messages, model="qwen-plus")

# 使用压缩后的消息调用你的 LLM API
llm_response = requests.post(
    "https://your-llm-api.com/chat",
    json={
        "model": "qwen-plus",
        "messages": result['messages']  # 使用压缩后的消息
    }
)

print(f"节省了 {result['tokens_saved']} tokens!")
```

### 批量处理

```python
from compress.client import CompressClient

client = CompressClient()

conversations = [...]  # 多个对话

for conv in conversations:
    result = client.compress(conv, model="gpt-4o")
    # 处理压缩后的对话
    process(result['messages'])

# 查看总体统计
client.print_stats()
```

### RAG检索内容压缩

```python
from compress.client import CompressClient

client = CompressClient()

# 从向量数据库检索到的文档
documents = [
    {
        "content": "Python是一种高级编程语言...",
        "score": 0.95,
        "metadata": {"source": "python_intro.txt", "page": 1}
    },
    {
        "content": "FastAPI是一个现代Web框架...",
        "score": 0.88,
        "metadata": {"source": "fastapi_guide.txt", "page": 5}
    },
    # 更多文档...
]

user_query = "什么是Python？"

# 压缩RAG结果
result = client.compress_rag(
    documents=documents,
    query=user_query,
    top_k=3,           # 只保留前3个最相关的
    min_score=0.5,     # 过滤低分文档
    target_ratio=0.3,  # 每个文档压缩到30%
    model="gpt-4o"
)

print(f"保留文档数: {result['compressed_count']}")
print(f"Token节省: {result['tokens_saved']:,}")

# 使用压缩后的文档构建prompt
context = "\n\n".join([doc['content'] for doc in result['documents']])
final_prompt = f"问题: {user_query}\n\n相关文档:\n{context}"

# 发送给LLM
# llm_response = your_llm_api.chat(messages=[{"role": "user", "content": final_prompt}])
```

完整RAG示例请查看 `compress/rag_example.py`：

```bash
# 运行RAG压缩示例
python -m compress.rag_example
```

## 性能优化

- 首次调用会下载 Kompress 模型（~110MB ONNX INT8）
- 后续调用使用缓存，压缩速度很快
- 服务器默认使用 ONNX CPU 后端，无需 GPU
- 并发请求会自动限流，避免内存溢出

## 故障排除

### 无法连接服务器

```bash
# 检查服务器是否运行
curl http://localhost:8787/health

# 检查端口是否被占用
lsof -i :8787
```

### 模型下载失败

```bash
# 设置 HuggingFace 镜像（如需要）
export HF_ENDPOINT=https://huggingface.co

# 或使用本地模型
export HEADROOM_KOMPRESS_MODEL=/path/to/local/model
```

## 许可证

MIT License
