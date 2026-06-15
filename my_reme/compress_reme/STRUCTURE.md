# compress_reme 项目结构说明

## 📁 完整目录树

```
compress_reme/                      # 项目根目录
│
├── compress_reme/                  # 主代码包
│   ├── __init__.py                # 包初始化，导出公共接口
│   ├── __main__.py                # 入口文件，支持 python -m compress_reme
│   │
│   ├── core/                      # 核心模块
│   │   ├── __init__.py           # 导出核心组件
│   │   ├── models.py             # Pydantic 数据模型定义
│   │   └── session_manager.py    # Session 生命周期管理
│   │
│   ├── server/                    # 服务器模块
│   │   ├── __init__.py           # 导出服务器组件
│   │   └── app.py                # FastAPI 应用和路由
│   │
│   └── client/                    # 客户端模块
│       ├── __init__.py           # 导出客户端
│       └── client.py             # Python SDK 实现
│
├── examples/                       # 示例代码
│   ├── __init__.py
│   ├── basic_usage.py            # 基础使用示例（6个场景）
│   └── config_example.py         # 配置示例（多种LLM）
│
├── tests/                          # 测试代码
│   ├── __init__.py
│   └── test_install.py           # 安装和依赖测试
│
├── docs/                           # 详细文档
│   ├── README.md                 # 完整功能文档和API说明
│   ├── QUICKSTART.md             # 快速开始指南
│   ├── PROJECT.md                # 项目概览和架构设计
│   └── CONFIG_GUIDE.md           # LLM配置详细指南
│
├── scripts/                        # 运行脚本
│   ├── run_server.sh             # Unix/macOS启动脚本
│   └── run_server.bat            # Windows启动脚本
│
├── README.md                       # 项目主README（概览）
├── STRUCTURE.md                    # 本文件：结构说明
├── pyproject.toml                  # 项目配置和元数据
├── requirements.txt                # Python依赖列表
├── .env.example                    # 环境变量模板
└── .gitignore                      # Git忽略规则
```

## 📦 模块职责

### compress_reme/ - 主代码包

#### core/ - 核心模块
- **models.py** (3.5KB)
  - 定义所有 API 的请求和响应模型
  - 使用 Pydantic 进行数据验证
  - 包含：Message, CreateSessionRequest/Response, CompactRequest/Response 等

- **session_manager.py** (8.4KB)
  - SessionInfo: 单个会话信息类
  - SessionManager: 管理多个 ReMeLight 实例
  - 功能：创建/删除/获取会话、统计信息、环境变量配置

#### server/ - 服务器模块
- **app.py** (15.3KB)
  - FastAPI 应用定义
  - 11个 API 端点实现
  - 启动/关闭事件处理
  - .env 文件加载和配置检查

#### client/ - 客户端模块
- **client.py** (11.3KB)
  - ReMeClient 类：封装所有 HTTP API 调用
  - 简化的 Python 接口
  - 错误处理和响应解析

### examples/ - 示例代码

- **basic_usage.py** (10KB)
  - 6个完整的使用示例
  - 基础工作流、长对话压缩、摘要生成、记忆搜索、多会话管理、Tool压缩

- **config_example.py** (3KB)
  - 演示各种 LLM 配置方式
  - OpenAI、通义千问、DeepSeek、本地模型等

### tests/ - 测试代码

- **test_install.py** (2.4KB)
  - 验证所有依赖是否正确安装
  - 测试包导入
  - 提供诊断信息

### docs/ - 文档

- **README.md** (10.6KB)
  - 完整功能文档
  - API 端点详细说明
  - 使用场景和示例
  - 高级配置和故障排除

- **QUICKSTART.md** (6KB)
  - 5分钟快速上手
  - 从安装到运行的完整流程
  - 常见问题解答

- **PROJECT.md** (6.5KB)
  - 项目定位和核心特点
  - 系统架构设计
  - 技术栈说明
  - 部署方案

- **CONFIG_GUIDE.md** (4KB)
  - 大模型配置详细指南
  - 环境变量说明
  - 多种 LLM 提供商配置示例
  - 故障排除

## 🔄 导入关系

### 包导入层次
```python
# 顶层包
from compress_reme import ReMeClient, SessionManager, SessionInfo

# 等价于
from compress_reme.client import ReMeClient
from compress_reme.core import SessionManager, SessionInfo

# 子模块导入
from compress_reme.core.models import Message, CompactRequest
from compress_reme.server.app import app
```

### 内部导入关系
```
compress_reme/__init__.py
    ↓ imports
compress_reme/client/__init__.py
    ↓ imports
compress_reme/client/client.py (纯外部依赖，无内部导入)

compress_reme/core/__init__.py
    ↓ imports
compress_reme/core/models.py (Pydantic models)
compress_reme/core/session_manager.py (依赖ReMe)

compress_reme/server/__init__.py
    ↓ imports
compress_reme/server/app.py
    ↓ imports
compress_reme/core/models.py
compress_reme/core/session_manager.py
```

## 🚀 运行方式

### 1. 作为包运行（推荐）
```bash
# 安装
pip install -e .

# 启动服务器
python -m compress_reme
# 或
compress-reme-server

# 运行示例
compress-reme-example
```

### 2. 直接运行脚本
```bash
# 启动服务器
cd scripts
./run_server.sh  # macOS/Linux
run_server.bat   # Windows

# 或直接运行
python compress_reme/server/app.py
```

### 3. 作为库使用
```python
# 在其他项目中
from compress_reme import ReMeClient

client = ReMeClient("http://localhost:8788")
# ...
```

## 📝 文件大小统计

| 模块 | 文件 | 大小 | 说明 |
|------|------|------|------|
| core | models.py | 3.5KB | 数据模型 |
| core | session_manager.py | 8.4KB | Session管理 |
| server | app.py | 15.3KB | FastAPI应用 |
| client | client.py | 11.3KB | Python SDK |
| examples | basic_usage.py | 10KB | 使用示例 |
| examples | config_example.py | 3KB | 配置示例 |
| tests | test_install.py | 2.4KB | 测试脚本 |
| docs | README.md | 10.6KB | 完整文档 |
| docs | QUICKSTART.md | 6KB | 快速开始 |
| docs | PROJECT.md | 6.5KB | 项目概览 |
| docs | CONFIG_GUIDE.md | 4KB | 配置指南 |
| **总计** | | **~81KB** | 纯代码和文档 |

## 🎯 设计原则

### 1. 分层架构
- **core**: 核心业务逻辑，无Web依赖
- **server**: Web层，依赖core
- **client**: 客户端层，独立于server

### 2. 单一职责
- 每个模块专注一个功能领域
- models 只定义数据结构
- session_manager 只管理会话
- app 只处理 HTTP 请求

### 3. 依赖倒置
- server 依赖 core，而不是反过来
- client 不依赖 server 实现
- examples 依赖 client，不直接依赖 server

### 4. 开闭原则
- 通过继承和组合扩展功能
- 不修改核心代码，通过配置改变行为

## 🔧 扩展指南

### 添加新的 API 端点
1. 在 `core/models.py` 定义请求/响应模型
2. 在 `server/app.py` 添加路由处理函数
3. 在 `client/client.py` 添加客户端方法
4. 在 `examples/` 添加使用示例
5. 更新 `docs/README.md` API 文档

### 添加新的核心功能
1. 在 `core/` 创建新模块
2. 在 `core/__init__.py` 导出
3. 在 `server/app.py` 中使用
4. 编写测试
5. 更新文档

## 📚 参考

- [FastAPI最佳实践](https://fastapi.tiangolo.com/tutorial/)
- [Python包结构](https://packaging.python.org/en/latest/)
- [项目布局指南](https://docs.python-guide.org/writing/structure/)
