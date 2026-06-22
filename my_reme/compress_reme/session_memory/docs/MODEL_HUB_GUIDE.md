# Model Hub 配置指南

## 📋 概述

Model Hub 是一个多模型配置中心，允许你在一个配置文件中管理多个LLM模型，并灵活切换使用。

## 🎯 设计理念

### 传统方式（单一模型）
```yaml
llm:
  api_key: xxx
  base_url: xxx
  model: gpt-4
  temperature: 0.1
```

**问题：**
- ❌ 只能配置一个模型
- ❌ 切换模型需要修改多处配置
- ❌ 无法同时管理多个模型配置

### Model Hub方式（多模型中心）
```yaml
model_hub:
  gpt4:
    api_key: xxx
    base_url: xxx
    model_name: gpt-4
    temperature: 0.1
  
  gpt35:
    api_key: xxx
    model_name: gpt-3.5-turbo
    temperature: 0.7

llm:
  selected_model: gpt4  # 选择使用哪个模型
```

**优势：**
- ✅ 支持多个模型配置
- ✅ 一键切换模型
- ✅ 集中管理模型配置
- ✅ 支持不同厂商的模型

## 📝 配置格式

### 完整配置示例

```yaml
# config/config.yml

# 模型配置中心
model_hub:
  # 模型1: OpenAI GPT-4
  gpt4:
    api_key: "${LLM_API_KEY}"
    base_url: "${LLM_BASE_URL:https://api.openai.com/v1}"
    model_name: "gpt-4"
    temperature: 0.1
    max_tokens: 1024
    timeout: 60
    max_retries: 2
  
  # 模型2: OpenAI GPT-3.5
  gpt35:
    api_key: "${LLM_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 2000
    timeout: 60
    max_retries: 2
  
  # 模型3: 自定义模型（例如：本地部署的模型）
  local_llm:
    api_key: "your-local-key"
    base_url: "http://localhost:8000/v1"
    model_name: "llama-2-70b"
    temperature: 0.5
    max_tokens: 1500
    timeout: 120
    max_retries: 3
  
  # 模型4: 其他厂商（例如：Azure OpenAI）
  azure_gpt:
    api_key: "${AZURE_API_KEY}"
    base_url: "${AZURE_BASE_URL}"
    model_name: "gpt-35-turbo"
    temperature: 0.3
    max_tokens: 1000
    timeout: 60
    max_retries: 2

# LLM配置 - 选择使用哪个模型
llm:
  selected_model: "${LLM_SELECTED_MODEL:gpt4}"
```

### 配置字段说明

每个模型配置包含以下字段：

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `api_key` | string | ✅ | API密钥 | `"sk-xxx"` |
| `base_url` | string | ✅ | API基础URL | `"https://api.openai.com/v1"` |
| `model_name` | string | ✅ | 模型名称 | `"gpt-4"` |
| `temperature` | float | ✅ | 温度参数(0-2) | `0.1` |
| `max_tokens` | int | ✅ | 最大token数 | `1024` |
| `timeout` | int | ❌ | 超时时间(秒) | `60` |
| `max_retries` | int | ❌ | 最大重试次数 | `2` |

## 🚀 使用方式

### 1. 环境变量切换模型

```bash
# 方法1: 直接设置环境变量
export LLM_SELECTED_MODEL=gpt35
python -m __main__

# 方法2: 在.env文件中设置
echo "LLM_SELECTED_MODEL=gpt35" >> .env
python -m __main__

# 方法3: 运行时指定
LLM_SELECTED_MODEL=local_llm python -m __main__
```

### 2. 代码中使用

```python
from config import get_config

# 获取配置实例
cfg = get_config()

# 查看当前选中的模型
selected_model = cfg.get_selected_model_name()
print(f"当前模型: {selected_model}")  # 输出: gpt4

# 获取当前模型的配置
model_config = cfg.get_model_config()
print(model_config)
# {
#   "api_key": "sk-xxx",
#   "base_url": "https://api.openai.com/v1",
#   "model_name": "gpt-4",
#   "temperature": 0.1,
#   ...
# }

# 获取指定模型的配置
gpt35_config = cfg.get_model_config("gpt35")
print(gpt35_config)

# 列出所有可用的模型
available_models = cfg.list_available_models()
print(available_models)  # ['gpt4', 'gpt35', 'local_llm', 'azure_gpt']
```

### 3. 初始化LLM客户端

```python
from config import get_config
from core.llm_client import LlmClient

# 自动使用selected_model指定的模型
cfg = get_config()
model_config = cfg.get_model_config()
llm_client = LlmClient(model_config)

# 或者使用指定的模型
gpt35_config = cfg.get_model_config("gpt35")
llm_client = LlmClient(gpt35_config)
```

## 📊 常见场景

### 场景1: 开发和生产使用不同模型

```yaml
model_hub:
  # 开发环境：快速便宜的模型
  dev_model:
    api_key: "${LLM_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 1000
  
  # 生产环境：高质量模型
  prod_model:
    api_key: "${PROD_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-4"
    temperature: 0.1
    max_tokens: 2000

llm:
  selected_model: "${ENVIRONMENT:dev_model}"
```

### 场景2: 不同任务使用不同模型

```python
from config import get_config

cfg = get_config()

# 任务1: 对话生成（使用gpt4）
chat_config = cfg.get_model_config("gpt4")
chat_client = LlmClient(chat_config)

# 任务2: 摘要生成（使用gpt35，更快更便宜）
summary_config = cfg.get_model_config("gpt35")
summary_client = LlmClient(summary_config)

# 任务3: 代码生成（使用专门的代码模型）
code_config = cfg.get_model_config("codellama")
code_client = LlmClient(code_config)
```

### 场景3: 本地和云端模型混合

```yaml
model_hub:
  # 云端模型：高质量
  cloud_gpt4:
    api_key: "${OPENAI_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-4"
    temperature: 0.1
    max_tokens: 1024
  
  # 本地模型：隐私保护
  local_llama:
    api_key: "local"
    base_url: "http://localhost:8000/v1"
    model_name: "llama-2-70b"
    temperature: 0.5
    max_tokens: 1500

llm:
  selected_model: "local_llama"  # 默认使用本地模型保护隐私
```

## 🔧 高级用法

### 动态切换模型

```python
from config import get_config

cfg = get_config()

# 运行时切换模型
cfg.set('llm.selected_model', 'gpt35')

# 重新获取配置
model_config = cfg.get_model_config()
print(f"切换到: {cfg.get_selected_model_name()}")
```

### 添加新模型

```python
from config import get_config

cfg = get_config()

# 添加新模型配置
new_model = {
    "api_key": "new-key",
    "base_url": "https://new-api.com/v1",
    "model_name": "new-model",
    "temperature": 0.5,
    "max_tokens": 1500,
    "timeout": 60,
    "max_retries": 2
}

cfg.set('model_hub.new_model', new_model)

# 使用新模型
cfg.set('llm.selected_model', 'new_model')
```

### 批量测试多个模型

```python
from config import get_config
from core.llm_client import LlmClient

cfg = get_config()
test_message = "请简单介绍一下你自己"

# 遍历所有模型进行测试
for model_name in cfg.list_available_models():
    print(f"\n测试模型: {model_name}")
    
    try:
        model_config = cfg.get_model_config(model_name)
        client = LlmClient(model_config)
        
        result = client.do_llm(
            messages=[{"role": "user", "content": test_message}],
            model_name=model_config["model_name"]
        )
        
        print(f"✅ 成功: {result['content'][:50]}...")
    except Exception as e:
        print(f"❌ 失败: {e}")
```

## 🌍 环境变量

支持的环境变量：

```bash
# 基础配置（适用于所有OpenAI兼容模型）
LLM_API_KEY=sk-xxx                    # API密钥
LLM_BASE_URL=https://api.openai.com/v1  # API基础URL
LLM_SELECTED_MODEL=gpt4               # 选择使用的模型

# 自定义模型配置
CUSTOM_API_KEY=custom-key
CUSTOM_BASE_URL=https://custom.com/v1

# Azure配置示例
AZURE_API_KEY=azure-key
AZURE_BASE_URL=https://xxx.openai.azure.com/
```

## ✅ 最佳实践

### 1. 命名规范

```yaml
model_hub:
  gpt4          # ✅ 简短清晰
  openai_gpt35  # ✅ 带厂商前缀
  prod_model    # ✅ 表明用途
  
  model1        # ❌ 不够描述性
  m             # ❌ 太简短
```

### 2. 敏感信息管理

```yaml
# ✅ 推荐：使用环境变量
model_hub:
  gpt4:
    api_key: "${LLM_API_KEY}"
    base_url: "${LLM_BASE_URL:https://api.openai.com/v1}"

# ❌ 不推荐：硬编码密钥
model_hub:
  gpt4:
    api_key: "sk-xxxxxxxxxxxxxxxx"
```

### 3. 参数合理配置

```yaml
model_hub:
  # 需要准确性的场景
  precise_model:
    temperature: 0.1   # ✅ 低温度，更确定性
    max_tokens: 1024
  
  # 需要创造性的场景
  creative_model:
    temperature: 0.9   # ✅ 高温度，更多样性
    max_tokens: 2000
```

### 4. 超时和重试配置

```yaml
model_hub:
  # 快速API
  fast_model:
    timeout: 30       # ✅ 短超时
    max_retries: 2
  
  # 慢速API或大模型
  slow_model:
    timeout: 120      # ✅ 长超时
    max_retries: 3
```

## 📖 API参考

### Config类方法

```python
# 获取配置实例
cfg = get_config()

# 获取模型配置
model_config = cfg.get_model_config(model_name=None)
# 参数: model_name - 模型名称，None则使用selected_model
# 返回: Dict - 模型配置字典

# 列出所有模型
models = cfg.list_available_models()
# 返回: List[str] - 模型名称列表

# 获取选中的模型名
name = cfg.get_selected_model_name()
# 返回: str - 当前选中的模型名称

# 向后兼容方法
llm_config = cfg.get_llm_config()
# 返回: Dict - 等同于get_model_config()
```

## 🔍 故障排除

### 问题1: 模型未找到

```python
# 错误
ValueError: 模型 'xxx' 在 model_hub 中未找到

# 解决
cfg = get_config()
print(f"可用模型: {cfg.list_available_models()}")
# 检查模型名是否存在于列表中
```

### 问题2: 环境变量未替换

```yaml
# 配置
model_hub:
  gpt4:
    api_key: "${LLM_API_KEY}"

# 检查
echo $LLM_API_KEY  # 确保环境变量已设置
```

### 问题3: 选中的模型无效

```bash
# 错误的环境变量
export LLM_SELECTED_MODEL=invalid_model

# 检查配置文件中是否有该模型
```

## 📚 示例代码

完整示例: [examples/model_hub_usage.py](../examples/model_hub_usage.py)

```python
"""Model Hub使用示例"""
from config import get_config
from core.llm_client import LlmClient

def main():
    cfg = get_config()
    
    # 1. 查看可用模型
    print("可用模型:", cfg.list_available_models())
    
    # 2. 获取当前模型
    current = cfg.get_selected_model_name()
    print(f"当前模型: {current}")
    
    # 3. 使用当前模型
    config = cfg.get_model_config()
    client = LlmClient(config)
    
    # 4. 调用LLM
    result = client.do_llm(
        messages=[{"role": "user", "content": "你好"}],
        model_name=config["model_name"]
    )
    print(f"回复: {result['content']}")

if __name__ == "__main__":
    main()
```

## 🎯 总结

Model Hub配置系统的核心优势：

1. **灵活性** - 支持多个模型，一键切换
2. **可维护性** - 集中管理，配置清晰
3. **扩展性** - 易于添加新模型
4. **兼容性** - 向后兼容旧配置方式
5. **安全性** - 支持环境变量，保护敏感信息

通过Model Hub，你可以轻松管理和切换不同的LLM模型，满足各种业务场景需求。
