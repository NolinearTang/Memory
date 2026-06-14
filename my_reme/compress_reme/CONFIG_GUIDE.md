# 配置指南

## 大模型配置说明

compress_reme 需要配置 LLM API 才能正常工作，主要用于：
- 对话压缩
- 摘要生成  
- 记忆搜索

## 配置方式（3种）

### 方式 1: 使用 `.env` 文件（推荐）⭐

#### 第一步：创建配置文件

```bash
# 在 compress_reme 目录下
cd compress_reme

# 复制示例文件
cp .env.example .env
```

#### 第二步：编辑 `.env` 文件

```bash
# LLM API 配置（必需）
LLM_API_KEY=sk-your-openai-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o

# Embedding API 配置（可选，用于语义搜索）
EMBEDDING_API_KEY=sk-your-openai-api-key-here
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL_NAME=text-embedding-ada-002
```

#### 第三步：启动服务器

```bash
python -m compress_reme.reme_server
```

服务器会自动加载 `.env` 文件中的配置。

---

### 方式 2: 系统环境变量

#### Linux/macOS

```bash
# 设置环境变量
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL_NAME="gpt-4o"

# 启动服务器
python -m compress_reme.reme_server
```

#### Windows (PowerShell)

```powershell
$env:LLM_API_KEY="your-api-key"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL_NAME="gpt-4o"

python -m compress_reme.reme_server
```

---

### 方式 3: 创建会话时指定

不设置全局配置，在创建每个会话时指定：

```python
from compress_reme.reme_client import ReMeClient

client = ReMeClient()

# 创建会话时指定 LLM 配置
client.create_session(
    session_id="my_session",
    llm_config={
        "model_name": "gpt-4o",
        "api_key": "your-api-key",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 4000,
    }
)
```

---

## 不同 LLM 提供商配置

### OpenAI

```bash
LLM_API_KEY=sk-your-openai-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o
```

### 阿里云通义千问

```bash
LLM_API_KEY=your-dashscope-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus
```

### DeepSeek

```bash
LLM_API_KEY=your-deepseek-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
```

### Ollama (本地模型)

```bash
# Ollama 默认不需要 API Key
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=llama3
```

---

## 配置验证

### 启动服务器时检查日志

```bash
python -m compress_reme.reme_server
```

正确配置会显示：
```
✅ LLM API 配置已加载
Default LLM config: model=gpt-4o
```

未配置会显示：
```
⚠️  未设置 LLM_API_KEY 环境变量！
   请在 .env 文件中配置或设置环境变量
```

---

## 配置优先级

当多种配置方式同时存在时，优先级如下：

1. **会话级配置** - `create_session(llm_config=...)`
2. **环境变量** - `.env` 文件或系统环境变量
3. **默认配置** - SessionManager 初始化参数

---

## 故障排除

### 问题 1: 服务器启动提示未设置 API Key

**症状**：
```
⚠️  未设置 LLM_API_KEY 环境变量！
```

**解决方案**：
1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中是否设置了 `LLM_API_KEY`
3. 确保工作目录是 `compress_reme`

### 问题 2: API 调用失败

**症状**：
```
Error: Invalid API Key
```

**解决方案**：
1. 检查 API Key 是否正确
2. 检查 Base URL 是否正确
3. 检查 API Key 是否有权限

---

## 环境变量完整列表

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `LLM_API_KEY` | ✅ | - | LLM API 密钥 |
| `LLM_BASE_URL` | ⭐ | - | LLM API 基础 URL |
| `LLM_MODEL_NAME` | ⭐ | - | LLM 模型名称 |
| `EMBEDDING_API_KEY` | ❌ | - | Embedding API 密钥 |
| `EMBEDDING_BASE_URL` | ❌ | - | Embedding API 基础 URL |
| `EMBEDDING_MODEL_NAME` | ❌ | - | Embedding 模型名称 |

**说明**：
- ✅ 必需
- ⭐ 强烈推荐
- ❌ 可选
