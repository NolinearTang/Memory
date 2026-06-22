# Model Hub 配置重构说明

## 📋 更新概述

将单一LLM配置升级为**Model Hub多模型配置中心**，支持在一个配置文件中管理多个LLM模型并灵活切换。

## 🔄 配置变化

### 旧配置格式 (v1.0)

```yaml
llm:
  api_key: "${LLM_API_KEY}"
  base_url: "${LLM_BASE_URL:https://api.openai.com/v1}"
  model: "${LLM_MODEL:gpt-4}"
  timeout: 60
  max_retries: 2
  temperature: 0.1
  max_tokens: 1024
```

### 新配置格式 (v1.1)

```yaml
# 模型配置中心
model_hub:
  # 模型1
  gpt4:
    api_key: "${LLM_API_KEY}"
    base_url: "${LLM_BASE_URL:https://api.openai.com/v1}"
    model_name: "gpt-4"
    temperature: 0.1
    max_tokens: 1024
    timeout: 60
    max_retries: 2
  
  # 模型2
  gpt35:
    api_key: "${LLM_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 2000
    timeout: 60
    max_retries: 2
  
  # 可以添加更多模型...

# 选择使用哪个模型
llm:
  selected_model: "${LLM_SELECTED_MODEL:gpt4}"
```

## ✨ 新增功能

### 1. 配置文件 (config/config.yml)

- ✅ 新增 `model_hub` 配置段
- ✅ 预配置 `gpt4`, `gpt35`, `custom_model` 三个模型
- ✅ `llm.selected_model` 用于选择当前使用的模型

### 2. Config类新增方法 (config/config.py)

```python
# 获取指定模型的配置
model_config = cfg.get_model_config(model_name=None)

# 列出所有可用模型
models = cfg.list_available_models()

# 获取当前选中的模型名称
current = cfg.get_selected_model_name()
```

### 3. 应用启动 (app.py)

- ✅ 自动从 `model_hub` 加载配置
- ✅ 启动时显示当前使用的模型
- ✅ 显示所有可用的模型列表

### 4. 文档

- 📚 `docs/MODEL_HUB_GUIDE.md` - 完整使用指南
- 📝 `examples/model_hub_usage.py` - 使用示例代码

## 🚀 使用方式

### 方式1: 环境变量切换

```bash
# 使用gpt4（默认）
python -m __main__

# 切换到gpt35
export LLM_SELECTED_MODEL=gpt35
python -m __main__

# 切换到自定义模型
export LLM_SELECTED_MODEL=custom_model
python -m __main__
```

### 方式2: 修改配置文件

编辑 `config/config.yml`:
```yaml
llm:
  selected_model: "gpt35"  # 改为想要使用的模型
```

### 方式3: 代码中动态切换

```python
from config import get_config

cfg = get_config()
cfg.set('llm.selected_model', 'gpt35')
```

## 📦 修改的文件

### 配置文件
- `config/config.yml` - 重构为model_hub格式
- `config/config.py` - 新增model_hub相关方法

### 应用代码
- `app.py` - 使用model_hub初始化LLM客户端

### 文档
- `docs/MODEL_HUB_GUIDE.md` - 新增完整指南
- `MODEL_HUB_CHANGELOG.md` - 本文件

### 示例
- `examples/model_hub_usage.py` - 新增使用示例

## 🔄 向后兼容

### 保留的方法

```python
# 旧方法仍然可用
llm_config = cfg.get_llm_config()  
# 等同于: cfg.get_model_config()
```

### 环境变量兼容

```bash
# 仍然支持旧的环境变量
export LLM_API_KEY=xxx
export LLM_BASE_URL=xxx

# 新增环境变量
export LLM_SELECTED_MODEL=gpt4  # 选择模型
```

## 📊 对比优势

| 特性 | 旧方式 | 新方式 (Model Hub) |
|------|--------|-------------------|
| 支持模型数量 | 1个 | 无限制 |
| 切换模型 | 修改多处配置 | 一个环境变量 |
| 管理复杂度 | 分散 | 集中管理 |
| 多模型对比 | ❌ 不支持 | ✅ 支持 |
| 不同场景 | ❌ 单一配置 | ✅ 灵活配置 |
| 扩展性 | 低 | 高 |

## 🎯 使用场景

### 场景1: 开发/生产环境分离

```yaml
model_hub:
  dev_model:
    model_name: "gpt-3.5-turbo"  # 开发用便宜快速的模型
  prod_model:
    model_name: "gpt-4"          # 生产用高质量模型
```

### 场景2: 不同任务使用不同模型

```python
# 对话任务用GPT-4
chat_config = cfg.get_model_config("gpt4")

# 摘要任务用GPT-3.5
summary_config = cfg.get_model_config("gpt35")
```

### 场景3: 本地和云端混合

```yaml
model_hub:
  cloud_gpt4:
    base_url: "https://api.openai.com/v1"
  local_llama:
    base_url: "http://localhost:8000/v1"
```

## 🧪 测试

### 运行示例代码

```bash
cd examples
python model_hub_usage.py
```

### 查看可用模型

```bash
cd session_memory
python -c "from config import get_config; print(get_config().list_available_models())"
```

### 测试模型切换

```bash
# 测试gpt4
export LLM_SELECTED_MODEL=gpt4
python -m __main__

# 测试gpt35
export LLM_SELECTED_MODEL=gpt35
python -m __main__
```

## 💡 最佳实践

### 1. 敏感信息使用环境变量

```yaml
model_hub:
  gpt4:
    api_key: "${LLM_API_KEY}"  # ✅ 推荐
    # api_key: "sk-xxx"        # ❌ 不推荐硬编码
```

### 2. 合理命名模型

```yaml
model_hub:
  gpt4:           # ✅ 简短清晰
  prod_gpt4:      # ✅ 表明用途
  openai_gpt35:   # ✅ 带厂商前缀
```

### 3. 根据场景配置参数

```yaml
model_hub:
  # 需要准确性
  precise_model:
    temperature: 0.1
  
  # 需要创造性
  creative_model:
    temperature: 0.9
```

## 📚 相关文档

- **完整指南**: [docs/MODEL_HUB_GUIDE.md](docs/MODEL_HUB_GUIDE.md)
- **使用示例**: [examples/model_hub_usage.py](../examples/model_hub_usage.py)
- **配置文件**: [config/config.yml](config/config.yml)

## 🔮 未来计划

- [ ] 支持模型自动切换（失败回退）
- [ ] 添加模型性能监控
- [ ] 支持模型负载均衡
- [ ] 添加模型成本统计
- [ ] Web界面选择模型

## ❓ 常见问题

### Q1: 如何添加新模型？

在 `config/config.yml` 的 `model_hub` 下添加配置：

```yaml
model_hub:
  my_model:
    api_key: "xxx"
    base_url: "xxx"
    model_name: "xxx"
    temperature: 0.5
    max_tokens: 1500
```

### Q2: 如何切换模型？

```bash
export LLM_SELECTED_MODEL=my_model
```

### Q3: 旧代码是否需要修改？

不需要。`get_llm_config()` 方法仍然可用，会自动返回当前选中模型的配置。

### Q4: 如何列出所有模型？

```python
from config import get_config
models = get_config().list_available_models()
print(models)
```

## 📝 总结

Model Hub配置重构带来的核心价值：

- ✅ **灵活性** - 多模型管理，一键切换
- ✅ **可维护性** - 配置集中，结构清晰
- ✅ **扩展性** - 轻松添加新模型
- ✅ **兼容性** - 向后兼容，平滑升级
- ✅ **实用性** - 满足多场景需求

从单一模型配置升级到Model Hub，为项目的LLM使用提供了更强大、更灵活的管理能力。
