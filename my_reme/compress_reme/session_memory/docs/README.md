# Session Memory - 工控领域智能会话记忆系统

基于对话摘要和BM25检索的工控技术支持会话记忆服务，专为变频器、PLC、伺服系统等工控设备的故障诊断和技术支持场景设计。

## 核心特性

- ⚡ **快速响应** - add_message立即返回，后台异步处理
- 🤖 **智能摘要** - 工控领域专业摘要，准确提取技术要点
- 📝 **自动压缩** - 长回答（>200字）自动压缩，保留关键信息
- 🔍 **BM25检索** - 基于关键词的相关对话检索
- 💾 **持久化存储** - JSONL格式append-only存储
- 🔄 **滚动窗口** - 保留近3轮对话，旧对话自动摘要
- 📊 **状态管理** - 自动维护故障码、功能码、产品信息

## 快速开始

### 1. 安装依赖

```bash
cd session_memory
pip install fastapi uvicorn openai jieba python-dotenv
```

### 2. 配置环境变量

在上级目录创建 `.env` 文件：

```bash
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

### 3. 启动服务

```bash
# 方式1: 使用模块启动（推荐）
python -m session_memory

# 方式2: 指定端口
python -m session_memory --port 8789

# 方式3: Web启动脚本（自动打开浏览器）
cd frontend
./start_web.sh
```

### 4. 访问界面

- 🌐 **前端测试页面**: http://localhost:8789/
- 📚 **API文档**: http://localhost:8789/docs
- 💚 **健康检查**: http://localhost:8789/health

## 项目结构

```
session_memory/
├── README.md                # 本文档
├── PROMPTS_GUIDE.md         # Prompts配置指南
├── __init__.py              # 模块初始化
├── __main__.py              # 启动入口
├── models.py                # 数据模型
├── storage.py               # 数据持久化层
├── bm25_retriever.py        # BM25检索引擎
├── llm_client.py            # LLM调用客户端
├── summarizer.py            # 工控领域摘要生成器
├── session_manager.py       # 核心会话管理器
├── app.py                   # FastAPI服务器
├── prompts.json             # Prompts配置文件（可自定义）
├── prompts.json.example     # Prompts配置示例
├── test_api.py              # 单元测试
├── test_prompts.py          # Prompts配置测试
├── example_client.py        # HTTP客户端示例
└── frontend/                # 前端相关文件
    ├── index.html          # Web测试界面
    ├── WEB_UI_GUIDE.md     # Web UI使用指南
    └── start_web.sh        # 快速启动脚本
```

## API使用

### 1. add_message - 添加对话消息

```python
import requests

response = requests.post("http://localhost:8789/add_message", json={
    "session_id": "session_001",
    "messages": [
        {"role": "user", "content": "MD500变频器显示E001报警，怎么处理？"},
        {"role": "assistant", "content": "E001是过热保护报警..."}
    ],
    "fault_code": ["E001"],
    "function_code": ["F100"],
    "product_code": ["MD500"]
})
```

### 2. get_message - 获取对话上下文

```python
response = requests.post("http://localhost:8789/get_message", json={
    "session_id": "session_001",
    "query": "散热风扇"
})
```

返回内容包括：状态信息（产品、故障码、功能码）+ 上下文（摘要 + 近期对话 + 相关对话）

## Web UI 测试界面

```bash
cd frontend
./start_web.sh
```

详细使用说明：[frontend/WEB_UI_GUIDE.md](frontend/WEB_UI_GUIDE.md)

## 技术实现

### LLM调用

使用自定义的 `LlmClient` 进行大模型调用：
- 统一的配置管理（API Key、Base URL）
- 同步调用接口（通过asyncio.to_thread异步包装）
- 规范的错误处理和返回格式

### 工控领域专业摘要

所有摘要针对工控领域优化（temperature=0.1，确保严谨）：

**两种摘要策略：**
- **基础摘要** (≤6条消息): 150字以内，简洁提取要点
- **详细摘要** (>6条消息): 1000字以内，完整记录诊断过程

**摘要要求：**
1. 准确提取技术要点（设备型号、故障码、参数等）
2. 保留问题诊断的逻辑链条
3. 记录关键操作步骤和解决方案
4. 使用专业术语，避免歧义

## 自定义Prompts配置

所有摘要提示词都存储在 `prompts.json` 配置文件中，你可以随时修改而无需改代码。

### 快速修改

编辑 `prompts.json` 文件：

```bash
nano prompts.json
# 修改后重启服务生效
```

### 配置项说明

- **system_prompts**: AI的身份定义（如：工控专家）
- **user_prompts**: 具体的任务要求和字数限制
- **llm_parameters**: temperature和max_tokens控制

详细说明请查看：[PROMPTS_GUIDE.md](PROMPTS_GUIDE.md)

### 示例：修改字数限制

```json
{
  "user_prompts": {
    "multi_turn_summary": {
      "template": "...字数限制：不超过500字...",
      "max_chars": 500
    }
  },
  "llm_parameters": {
    "multi_turn_summary": {
      "max_tokens": 800
    }
  }
}
```

## 数据存储

```
.session_memory/
├── messages/
│   └── {session_id}.jsonl    # 对话消息（append-only）
└── metadata/
    └── {session_id}.json      # 会话元数据、摘要
```

## 测试

```bash
# 单元测试
python test_api.py

# HTTP客户端测试
python example_client.py
```

## 配置参数

```python
# session_manager.py
KEEP_RECENT = 3                # 保留近3轮对话

# summarizer.py  
max_length = 200               # 压缩阈值

# bm25_retriever.py
k1 = 1.5, b = 0.75            # BM25参数
```

## 常见问题

**Q: LLM API调用失败？**  
检查 `.env` 文件中的 `LLM_API_KEY`

**Q: 摘要未生成？**  
等待几秒让后台处理完成，确认对话轮数超过3轮

**Q: 前端页面打不开？**  
确认服务器已启动，检查 `frontend/index.html` 是否存在

## 依赖项

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
openai>=1.0.0
jieba>=0.42.1
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## License

MIT License
