# 项目重构说明

## 重构时间

2024-06-22

## 重构目标

将项目从扁平化结构重构为模块化、层次化的结构，提高代码可维护性和可扩展性。

## 重构前后对比

### 重构前（扁平结构）

```
session_memory/
├── __init__.py
├── __main__.py
├── app.py
├── models.py
├── storage.py
├── bm25_retriever.py
├── llm_client.py
├── summarizer.py
├── session_manager.py
├── prompts.json
├── test_api.py
├── test_prompts.py
├── example_client.py
├── README.md
├── PROMPTS_GUIDE.md
├── CHANGELOG.md
└── frontend/
```

**问题：**
- 所有文件混在一起，职责不清
- 文档和代码混合
- 测试和示例没有独立目录
- 缺少统一的配置管理
- Prompts模板没有独立管理

### 重构后（模块化结构）

```
session_memory/
├── __init__.py              # 模块入口
├── __main__.py              # 启动入口
├── app.py                   # FastAPI服务器
├── README.md                # 项目说明
├── requirements.txt         # 依赖项
│
├── config/                  # 📁 配置模块
│   ├── __init__.py
│   ├── config.py           # 配置管理类
│   └── config.yml          # YAML配置文件
│
├── core/                    # 📁 核心模块
│   ├── __init__.py
│   ├── models.py           # 数据模型
│   ├── storage.py          # 数据持久化
│   ├── llm_client.py       # LLM调用客户端
│   ├── summarizer.py       # 摘要生成器
│   └── session_manager.py  # 会话管理器
│
├── retrieval/               # 📁 检索模块
│   ├── __init__.py
│   ├── bm25_retriever.py          # BM25检索引擎
│   └── embedding_rerank_handler.py # Embedding检索
│
├── prompts/                 # 📁 Prompts模板
│   ├── prompts.json        # Prompts配置
│   └── prompts.json.example # 配置示例
│
├── docs/                    # 📁 文档
│   ├── README.md           # 详细文档
│   ├── PROMPTS_GUIDE.md    # Prompts配置指南
│   ├── CHANGELOG.md        # 更新日志
│   ├── WEB_UI_GUIDE.md     # Web UI使用指南
│   └── PROJECT_RESTRUCTURE.md # 本文档
│
├── tests/                   # 📁 测试
│   ├── __init__.py
│   ├── test_api.py         # API测试
│   └── test_prompts.py     # Prompts测试
│
├── examples/                # 📁 示例代码
│   └── example_client.py   # HTTP客户端示例
│
└── frontend/                # 📁 前端
    ├── index.html          # Web测试界面
    ├── WEB_UI_GUIDE.md     # Web UI指南
    └── start_web.sh        # 启动脚本
```

**优势：**
- ✅ 职责清晰，模块化设计
- ✅ 文档独立管理
- ✅ 配置统一管理（config.yml + config.py）
- ✅ 检索功能独立模块
- ✅ Prompts模板独立管理
- ✅ 测试和示例分离

## 主要改动

### 1. 配置模块 (config/)

**新增文件：**
- `config/config.yml` - YAML配置文件
- `config/config.py` - 配置管理类

**特性：**
- 支持环境变量替换 `${LLM_API_KEY}`
- 支持默认值 `${LLM_MODEL:gpt-4}`
- 点号访问 `config.get('llm.api_key')`
- 分类获取 `config.get_llm_config()`

**使用示例：**
```python
from session_memory.config import get_config

config = get_config()
api_key = config.get('llm.api_key')
temperature = config.get('llm.temperature', 0.1)
```

### 2. 核心模块 (core/)

**包含文件：**
- `models.py` - 数据模型
- `storage.py` - 存储层
- `llm_client.py` - LLM客户端
- `summarizer.py` - 摘要生成器
- `session_manager.py` - 会话管理器

**导入路径变化：**
```python
# 旧方式
from session_memory.models import Message
from session_memory.summarizer import ConversationSummarizer

# 新方式
from session_memory.core.models import Message
from session_memory.core.summarizer import ConversationSummarizer

# 或者通过主模块导入
from session_memory import Message, ConversationSummarizer
```

### 3. 检索模块 (retrieval/)

**包含文件：**
- `bm25_retriever.py` - BM25检索
- `embedding_rerank_handler.py` - Embedding检索

**用途：**
- 统一管理所有检索相关功能
- 便于扩展新的检索方法

### 4. Prompts模板 (prompts/)

**包含文件：**
- `prompts.json` - 当前使用的配置
- `prompts.json.example` - 配置示例

**路径更新：**
```python
# summarizer.py 中自动查找
prompts_file = Path(__file__).parent.parent / "prompts" / "prompts.json"
```

### 5. 文档模块 (docs/)

**包含文件：**
- `README.md` - 详细文档
- `PROMPTS_GUIDE.md` - Prompts配置指南
- `CHANGELOG.md` - 更新日志
- `WEB_UI_GUIDE.md` - Web UI使用指南
- `PROJECT_RESTRUCTURE.md` - 项目重构说明

**优势：**
- 所有文档集中管理
- 便于维护和查找

### 6. 测试模块 (tests/)

**包含文件：**
- `test_api.py` - API功能测试
- `test_prompts.py` - Prompts配置测试

**路径更新：**
```python
# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.summarizer import ConversationSummarizer
```

### 7. 示例模块 (examples/)

**包含文件：**
- `example_client.py` - HTTP客户端示例

**用途：**
- 提供使用示例
- 便于用户学习

## 导入路径更新

### 主模块 `__init__.py`

```python
from .core.session_manager import SessionMemoryManager
from .core.models import Message, AddMessageRequest
from .retrieval.bm25_retriever import BM25Retriever
from .config import get_config, Config
```

### app.py

```python
# 旧方式
from .session_manager import SessionMemoryManager
from .models import AddMessageRequest

# 新方式
from .core.session_manager import SessionMemoryManager
from .core.models import AddMessageRequest
from .config import get_config
```

### session_manager.py

```python
# 旧方式
from .bm25_retriever import BM25Retriever

# 新方式
from ..retrieval.bm25_retriever import BM25Retriever
```

### summarizer.py

```python
# 旧方式
prompts_file = Path(__file__).parent / "prompts.json"

# 新方式
prompts_file = Path(__file__).parent.parent / "prompts" / "prompts.json"
```

## 迁移指南

### 对于使用者

**如果你通过主模块导入，无需修改：**
```python
from session_memory import SessionMemoryManager, Message
```

**如果你直接导入子模块，需要更新路径：**
```python
# 旧方式
from session_memory.models import Message

# 新方式
from session_memory.core.models import Message
# 或
from session_memory import Message
```

### 对于开发者

1. **配置管理**
   ```python
   # 推荐使用config模块
   from session_memory.config import get_config
   config = get_config()
   ```

2. **Prompts路径**
   ```python
   # 自动查找prompts/prompts.json
   summarizer = ConversationSummarizer()
   
   # 或指定路径
   summarizer = ConversationSummarizer(
       prompts_file="custom_prompts.json"
   )
   ```

3. **测试运行**
   ```bash
   cd tests
   python test_api.py
   python test_prompts.py
   ```

## 配置文件说明

### config.yml 示例

```yaml
llm:
  api_key: "${LLM_API_KEY}"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4"
  temperature: 0.1

storage:
  dir: ".session_memory"

session:
  keep_recent: 3
  compress_threshold: 200

retrieval:
  bm25:
    k1: 1.5
    b: 0.75
```

### 使用Config类

```python
from session_memory.config import get_config

config = get_config()

# 获取配置
api_key = config.get('llm.api_key')
keep_recent = config.get('session.keep_recent', 3)

# 设置配置
config.set('llm.temperature', 0.2)

# 获取分类配置
llm_config = config.get_llm_config()
storage_config = config.get_storage_config()
```

## 文件移动清单

| 旧位置 | 新位置 | 说明 |
|--------|--------|------|
| `models.py` | `core/models.py` | 核心数据模型 |
| `storage.py` | `core/storage.py` | 存储层 |
| `llm_client.py` | `core/llm_client.py` | LLM客户端 |
| `summarizer.py` | `core/summarizer.py` | 摘要生成器 |
| `session_manager.py` | `core/session_manager.py` | 会话管理器 |
| `bm25_retriever.py` | `retrieval/bm25_retriever.py` | BM25检索 |
| `embedding_rerank_handler.py` | `retrieval/embedding_rerank_handler.py` | Embedding检索 |
| `prompts.json` | `prompts/prompts.json` | Prompts配置 |
| `prompts.json.example` | `prompts/prompts.json.example` | 配置示例 |
| `README.md` | `docs/README.md` | 详细文档 |
| `PROMPTS_GUIDE.md` | `docs/PROMPTS_GUIDE.md` | Prompts指南 |
| `CHANGELOG.md` | `docs/CHANGELOG.md` | 更新日志 |
| `test_api.py` | `tests/test_api.py` | API测试 |
| `test_prompts.py` | `tests/test_prompts.py` | Prompts测试 |
| `example_client.py` | `examples/example_client.py` | 示例代码 |

## 新增文件

| 文件 | 说明 |
|------|------|
| `config/config.yml` | YAML配置文件 |
| `config/config.py` | 配置管理类 |
| `config/__init__.py` | 配置模块入口 |
| `core/__init__.py` | 核心模块入口 |
| `retrieval/__init__.py` | 检索模块入口 |
| `tests/__init__.py` | 测试模块入口 |
| `requirements.txt` | 依赖项列表 |
| `README.md` | 根目录说明文档 |
| `docs/PROJECT_RESTRUCTURE.md` | 本文档 |
| `docs/WEB_UI_GUIDE.md` | Web UI指南（复制） |

## 兼容性

### ✅ 向后兼容

通过主模块导入的代码**无需修改**：

```python
# 这些导入方式继续有效
from session_memory import SessionMemoryManager
from session_memory import Message
from session_memory import get_config
```

### ⚠️ 需要更新

直接导入子模块的代码需要更新路径：

```python
# 旧方式 ❌
from session_memory.models import Message

# 新方式 ✅
from session_memory.core.models import Message
# 或
from session_memory import Message
```

## 测试验证

### 1. 导入测试

```python
python -c "from session_memory import SessionMemoryManager; print('✅ 导入成功')"
```

### 2. 配置测试

```bash
python -m session_memory.config.config
```

### 3. API测试

```bash
cd tests
python test_api.py
```

### 4. 启动服务

```bash
python -m session_memory
```

## 未来扩展

新的模块化结构便于扩展：

- **新增检索方法** → `retrieval/new_retriever.py`
- **新增存储后端** → `core/new_storage.py`
- **新增LLM客户端** → `core/new_llm_client.py`
- **新增配置格式** → `config/config.json`

## 总结

此次重构实现了：

1. ✅ **模块化设计** - 职责清晰，易于维护
2. ✅ **配置集中管理** - config模块统一管理所有配置
3. ✅ **文档独立管理** - docs目录集中存放
4. ✅ **测试分离** - tests目录独立
5. ✅ **Prompts模板化** - prompts目录独立管理
6. ✅ **向后兼容** - 主模块导入方式不变
7. ✅ **扩展性强** - 新增功能更方便

**版本更新：** v1.0.0 → v1.1.0
