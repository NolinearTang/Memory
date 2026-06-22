# 简化配置使用指南

## 📋 设计理念

配置系统极其简单：
1. 加载 `config.yml`
2. 得到一个大字典 `kllm_config`  
3. 直接从 `kllm_config` 取配置

## 🔧 核心API

### 获取配置字典

```python
from config import get_config

# 获取配置字典
kllm_config = get_config()

# kllm_config 就是一个普通的Python字典
print(type(kllm_config))  # <class 'dict'>
```

## 📝 使用方式

### 1. 获取模型配置

```python
from config import get_config

kllm_config = get_config()

# 获取选中的模型名
selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')

# 获取模型配置
model_config = kllm_config.get('model_hub', {}).get(selected_model)

# model_config 是这样的字典:
# {
#   'api_key': 'sk-xxx',
#   'base_url': 'https://api.openai.com/v1',
#   'model_name': 'gpt-4',
#   'temperature': 0.1,
#   'max_tokens': 1024,
#   'timeout': 60,
#   'max_retries': 2
# }
```

### 2. 初始化LLM客户端

```python
from config import get_config
from core.llm_client import LlmClient

kllm_config = get_config()

# 获取模型配置
selected_model = kllm_config['llm']['selected_model']
model_config = kllm_config['model_hub'][selected_model]

# 直接传给LlmClient
client = LlmClient(model_config)
```

### 3. 获取其他配置

```python
kllm_config = get_config()

# 获取存储配置
storage_config = kllm_config.get('storage', {})
storage_dir = storage_config.get('dir', '.session_memory')

# 获取session配置
session_config = kllm_config.get('session', {})
keep_recent = session_config.get('keep_recent', 3)

# 获取检索配置
retrieval_config = kllm_config.get('retrieval', {})
bm25_config = retrieval_config.get('bm25', {})
k1 = bm25_config.get('k1', 1.5)
```

## 📖 配置文件结构

`config/config.yml`:

```yaml
# 模型配置中心
model_hub:
  gpt4:
    api_key: "${LLM_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-4"
    temperature: 0.1
    max_tokens: 1024
    timeout: 60
    max_retries: 2
  
  gpt35:
    api_key: "${LLM_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 2000

# 选择使用哪个模型
llm:
  selected_model: "${LLM_SELECTED_MODEL:gpt4}"

# 其他配置
storage:
  dir: ".session_memory"

session:
  keep_recent: 3
  compress_threshold: 200

retrieval:
  bm25:
    k1: 1.5
    b: 0.75
    top_k: 5
```

## 🚀 完整示例

### 示例1: 基础使用

```python
from config import get_config
from core.llm_client import LlmClient

# 1. 获取配置字典
kllm_config = get_config()

# 2. 查看所有可用模型
available_models = list(kllm_config['model_hub'].keys())
print(f"可用模型: {available_models}")

# 3. 获取当前选中的模型
selected = kllm_config['llm']['selected_model']
print(f"当前模型: {selected}")

# 4. 获取模型配置
model_config = kllm_config['model_hub'][selected]

# 5. 初始化LLM客户端
client = LlmClient(model_config)

# 6. 调用LLM
result = client.do_llm(
    messages=[{"role": "user", "content": "你好"}],
    model_name=model_config['model_name']
)
print(result['content'])
```

### 示例2: 切换模型

```python
from config import get_config
from core.llm_client import LlmClient

kllm_config = get_config()

# 方式1: 使用gpt4
model_config = kllm_config['model_hub']['gpt4']
client_gpt4 = LlmClient(model_config)

# 方式2: 使用gpt35
model_config = kllm_config['model_hub']['gpt35']
client_gpt35 = LlmClient(model_config)

# 方式3: 动态选择
model_name = 'gpt35'
model_config = kllm_config['model_hub'][model_name]
client = LlmClient(model_config)
```

### 示例3: 在app.py中使用

```python
from config import get_config
from core.llm_client import LlmClient

# 启动时初始化
kllm_config = get_config()

# 获取选中的模型
selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')

# 获取模型配置
model_config = kllm_config.get('model_hub', {}).get(selected_model)

if not model_config:
    raise ValueError(f"模型 '{selected_model}' 未找到")

# 初始化LLM客户端
llm_client = LlmClient(model_config)

# 使用
result = llm_client.do_llm(
    messages=[{"role": "user", "content": "测试"}],
    model_name=model_config['model_name'],
    temperature=model_config.get('temperature', 0.7),
    max_tokens=model_config.get('max_tokens', 1000)
)
```

## 🔄 环境变量支持

配置文件支持环境变量替换：

```yaml
model_hub:
  gpt4:
    api_key: "${LLM_API_KEY}"  # 从环境变量读取
    base_url: "${LLM_BASE_URL:https://api.openai.com/v1}"  # 带默认值

llm:
  selected_model: "${LLM_SELECTED_MODEL:gpt4}"  # 默认gpt4
```

使用方式：

```bash
# 设置环境变量
export LLM_API_KEY=sk-xxx
export LLM_SELECTED_MODEL=gpt35

# 运行程序
python -m __main__
```

## 📊 对比：旧方式 vs 新方式

### 旧方式（复杂）

```python
from config import get_config

cfg = get_config()  # 返回Config对象

# 需要调用各种方法
model_config = cfg.get_model_config('gpt4')
models = cfg.list_available_models()
selected = cfg.get_selected_model_name()

# 使用点号访问
value = cfg.get('llm.selected_model')
```

### 新方式（简单）

```python
from config import get_config

kllm_config = get_config()  # 返回字典

# 直接字典操作
model_config = kllm_config['model_hub']['gpt4']
models = list(kllm_config['model_hub'].keys())
selected = kllm_config['llm']['selected_model']

# 直接访问
value = kllm_config['llm']['selected_model']
```

## ✅ 核心优势

1. **简单** - 就是普通的Python字典
2. **直观** - 一眼能看懂
3. **灵活** - Python字典的所有操作都能用
4. **高效** - 没有额外的封装开销

## 💡 最佳实践

### 1. 安全地获取配置（使用.get()）

```python
# ✅ 推荐：带默认值
selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')

# ❌ 不推荐：可能KeyError
selected_model = kllm_config['llm']['selected_model']
```

### 2. 一次性获取多个配置

```python
# 获取所有需要的配置
storage_dir = kllm_config.get('storage', {}).get('dir', '.session_memory')
keep_recent = kllm_config.get('session', {}).get('keep_recent', 3)
top_k = kllm_config.get('retrieval', {}).get('bm25', {}).get('top_k', 5)
```

### 3. 在函数中传递配置

```python
def init_llm_client(kllm_config):
    """初始化LLM客户端"""
    selected_model = kllm_config['llm']['selected_model']
    model_config = kllm_config['model_hub'][selected_model]
    return LlmClient(model_config)

# 使用
kllm_config = get_config()
client = init_llm_client(kllm_config)
```

## 🔧 工具函数

如果需要，可以自己写辅助函数：

```python
def get_model_config(kllm_config, model_name=None):
    """获取指定模型的配置"""
    if model_name is None:
        model_name = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
    return kllm_config.get('model_hub', {}).get(model_name)

# 使用
kllm_config = get_config()
model_config = get_model_config(kllm_config)
model_config = get_model_config(kllm_config, 'gpt35')
```

## 📚 总结

配置系统现在非常简单：

```python
from config import get_config

# 1. 获取配置字典
kllm_config = get_config()

# 2. 直接使用Python字典操作
value = kllm_config['key1']['key2']
value = kllm_config.get('key1', {}).get('key2', 'default')

# 3. 传给需要的地方
client = LlmClient(kllm_config['model_hub']['gpt4'])
```

就是这么简单！✨
