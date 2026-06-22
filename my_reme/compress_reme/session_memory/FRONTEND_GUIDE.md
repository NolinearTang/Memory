# 前端启动和使用指南

## 🚀 前端启动（非常简单）

**前端不需要单独启动！** 前端是静态HTML，通过后端FastAPI服务器提供。

### 启动步骤

```bash
# 1. 进入项目目录
cd /path/to/session_memory

# 2. 启动后端服务（这就够了！）
python -m __main__

# 3. 浏览器访问前端页面
# http://localhost:8789/web       - 完整测试界面
# http://localhost:8789/chat-ui   - 简单聊天界面
```

就这么简单！**无需Node.js、npm或任何前端构建工具**。

## 📋 前端自动使用 config.yml 配置

前端会自动从后端获取配置信息，你只需要在 `config/config.yml` 中配置模型即可。

### 配置流程

#### 1. 编辑 config.yml

```yaml
# config/config.yml
model_hub:
  # 你的模型配置
  qwen:
    api_key: "sk-xxx"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model_name: "qwen3.6-35b-a3b"
    temperature: 0.01
    max_tokens: 1024

# 选择使用的模型
llm:
  selected_model: "qwen"
```

#### 2. 启动后端

```bash
python -m __main__

# 启动日志会显示：
# 📋 使用模型: qwen (qwen3.6-35b-a3b)
```

#### 3. 前端自动获取配置

打开 `http://localhost:8789/chat-ui`，前端会：
- 自动调用 `/config` API 获取配置
- 在页面标题显示当前模型名称
- 使用配置中的参数进行对话

### 配置API端点

后端提供了 `/config` 端点供前端获取配置：

```bash
# 查看当前配置
curl http://localhost:8789/config

# 响应示例
{
  "selected_model": "qwen",
  "model_name": "qwen3.6-35b-a3b",
  "temperature": 0.01,
  "max_tokens": 1024,
  "available_models": ["qwen", "gpt4", "gpt35"]
}
```

## 🌐 访问地址

启动后端后，通过以下地址访问：

| 页面 | URL | 说明 |
|------|-----|------|
| **API信息** | http://localhost:8789/ | 查看所有API端点 |
| **完整测试** | http://localhost:8789/web | Session Memory完整功能 |
| **简单聊天** | http://localhost:8789/chat-ui | 快速LLM对话（显示模型名） |
| **API文档** | http://localhost:8789/docs | Swagger交互式文档 |
| **配置查看** | http://localhost:8789/config | 当前模型配置（JSON） |

## 🔧 工作原理

### 架构图

```
┌─────────────────────────────────────┐
│  config/config.yml                  │
│  - model_hub配置                    │
│  - selected_model选择               │
└──────────────┬──────────────────────┘
               │
               ↓ 加载配置
┌─────────────────────────────────────┐
│  后端 FastAPI (app.py)              │
│  - 读取config.yml                   │
│  - 初始化LLM客户端                  │
│  - 提供API服务                      │
│  - 提供静态HTML文件                 │
└──────────────┬──────────────────────┘
               │
               ↓ 提供服务
┌─────────────────────────────────────┐
│  前端 (chat.html)                   │
│  1. 页面加载时调用 /config API      │
│  2. 获取当前模型配置                │
│  3. 显示模型名称                    │
│  4. 使用配置的参数调用 /chat API    │
└─────────────────────────────────────┘
```

### 代码示例

**前端获取配置：**
```javascript
// chat.html 中的代码
async function loadConfig() {
    const response = await fetch('http://localhost:8789/config');
    const config = await response.json();
    
    // 显示模型名称
    document.getElementById('modelInfo').textContent = 
        `(${config.model_name})`;
    
    console.log('当前配置:', config);
}

// 页面加载时自动获取
window.onload = function() {
    loadConfig();
};
```

**后端提供配置：**
```python
# app.py 中的代码
@app.get("/config")
async def get_current_config():
    kllm_config = get_config()
    selected_model = kllm_config.get('llm', {}).get('selected_model')
    model_config = kllm_config.get('model_hub', {}).get(selected_model)
    
    return {
        "selected_model": selected_model,
        "model_name": model_config.get('model_name'),
        "temperature": model_config.get('temperature'),
        "max_tokens": model_config.get('max_tokens'),
        "available_models": list(kllm_config.get('model_hub', {}).keys())
    }
```

## 🎯 使用场景

### 场景1: 快速测试

```bash
# 1. 修改配置
vim config/config.yml
# 选择模型: selected_model: "qwen"

# 2. 启动
python -m __main__

# 3. 浏览器打开
http://localhost:8789/chat-ui

# 4. 看到标题显示 "💬 LLM 对话测试 (qwen3.6-35b-a3b)"
```

### 场景2: 切换模型

```bash
# 1. 停止服务 (Ctrl+C)

# 2. 修改配置
vim config/config.yml
# 修改: selected_model: "gpt4"

# 3. 重新启动
python -m __main__

# 4. 刷新浏览器页面
# 标题自动更新为 "💬 LLM 对话测试 (gpt-4)"
```

### 场景3: 添加新模型

```yaml
# config/config.yml
model_hub:
  # 添加新模型
  my_custom_model:
    api_key: "xxx"
    base_url: "https://api.example.com/v1"
    model_name: "custom-llm"
    temperature: 0.5
    max_tokens: 2000

llm:
  selected_model: "my_custom_model"
```

```bash
# 重启服务
python -m __main__

# 前端自动使用新模型
http://localhost:8789/chat-ui
# 显示: "💬 LLM 对话测试 (custom-llm)"
```

## 🔍 验证配置

### 1. 查看后端日志

```bash
python -m __main__

# 输出：
# 📋 使用模型: qwen (qwen3.6-35b-a3b)
# ✅ LLM客户端初始化成功
```

### 2. 访问配置API

```bash
curl http://localhost:8789/config

# 输出：
{
  "selected_model": "qwen",
  "model_name": "qwen3.6-35b-a3b",
  "temperature": 0.01,
  "max_tokens": 1024,
  "available_models": ["qwen"]
}
```

### 3. 打开浏览器控制台

```javascript
// 在 http://localhost:8789/chat-ui 打开开发者工具
// 控制台会显示：
// 当前配置: {selected_model: "qwen", model_name: "qwen3.6-35b-a3b", ...}
```

## ❓ 常见问题

### Q1: 前端页面打不开？

**A:** 确保后端已启动：
```bash
python -m __main__
# 看到 "Session Memory服务器启动成功" 表示成功
```

### Q2: 前端显示的模型不对？

**A:** 检查配置并重启：
```bash
# 1. 检查配置
cat config/config.yml | grep selected_model

# 2. 重启后端
python -m __main__

# 3. 刷新浏览器页面 (Ctrl+R 或 F5)
```

### Q3: 修改config.yml后前端没变？

**A:** 需要重启后端服务：
```bash
# 1. 停止 (Ctrl+C)
# 2. 重启
python -m __main__
# 3. 刷新浏览器
```

### Q4: 能不能用其他端口？

**A:** 可以，修改启动参数：
```bash
python -m __main__ --port 9000

# 然后访问
http://localhost:9000/chat-ui
```

### Q5: 可以外网访问吗？

**A:** 可以，修改host：
```bash
python -m __main__ --host 0.0.0.0

# 然后通过IP访问
http://your-ip:8789/chat-ui
```

## 📝 总结

### 核心要点

1. **前端不需要单独启动** - 只启动后端即可
2. **自动读取配置** - 前端自动从 `/config` API 获取
3. **配置在config.yml** - 只需要编辑一个文件
4. **实时生效** - 重启后端后，前端自动更新

### 完整流程

```bash
# 1. 配置模型
vim config/config.yml

# 2. 启动后端
python -m __main__

# 3. 打开浏览器
http://localhost:8789/chat-ui

# 完成！前端自动使用config.yml中的配置
```

就是这么简单！🎉
