# compress_reme

基于 ReMe (Retrieval-enhanced Memory) 的 Session 级别对话压缩和记忆抽取服务。

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -e .

# 2. 启动服务器
python -m compress_reme
# 或
compress-reme-server

# 3. 查看 API 文档
# 访问 http://localhost:8788/docs
```

## 📁 项目结构

```
compress_reme/
├── compress_reme/          # 主代码包
│   ├── core/              # 核心模块
│   │   ├── models.py      # 数据模型
│   │   └── session_manager.py  # Session管理
│   ├── server/            # 服务器模块
│   │   └── app.py         # FastAPI应用
│   ├── client/            # 客户端模块
│   │   └── client.py      # Python SDK
│   ├── __init__.py
│   └── __main__.py        # 入口文件
├── examples/              # 示例代码
│   ├── basic_usage.py    # 基础使用示例
│   └── config_example.py # 配置示例
├── tests/                 # 测试代码
│   └── test_install.py   # 安装测试
├── docs/                  # 详细文档
│   ├── README.md         # 完整功能文档
│   ├── QUICKSTART.md     # 快速开始指南
│   ├── PROJECT.md        # 项目概览
│   └── CONFIG_GUIDE.md   # 配置指南
├── scripts/               # 运行脚本
│   ├── run_server.sh     # Unix启动脚本
│   └── run_server.bat    # Windows启动脚本
├── pyproject.toml         # 项目配置
├── requirements.txt       # 依赖列表
└── .gitignore            # Git忽略规则
```

## 📚 详细文档

- **[完整文档](docs/README.md)** - 功能特性、API 说明、使用示例
- **[快速开始](docs/QUICKSTART.md)** - 5分钟快速上手
- **[配置指南](docs/CONFIG_GUIDE.md)** - 大模型配置详解
- **[项目概览](docs/PROJECT.md)** - 架构设计、技术栈

## 🎯 核心功能

- ✅ **Session 管理** - 多会话隔离，每个会话独立管理对话上下文
- ✅ **对话压缩** - 基于 ReMe 的智能对话压缩（Tool结果压缩、记忆压缩）
- ✅ **摘要生成** - 自动生成对话摘要，提取关键信息
- ✅ **记忆搜索** - 语义搜索对话历史和记忆
- ✅ **HTTP API** - RESTful API 接口，支持跨语言调用
- ✅ **Python 客户端** - 简洁的 Python SDK

## 💡 使用示例

```python
from compress_reme.client import ReMeClient

# 创建客户端
client = ReMeClient()

# 创建会话
client.create_session("my_session")

# 添加消息
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
]
client.add_messages("my_session", messages)

# 压缩对话
result = client.compact("my_session")
print(f"节省了 {result['tokens_saved']} tokens!")

# 生成摘要
summary = client.summary("my_session")
print(f"摘要: {summary['summary']}")
```

更多示例请查看 [examples/](examples/) 目录。

## 🔧 配置

在项目根目录创建 `.env` 文件：

```bash
# LLM API 配置
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o
```

详细配置请查看 [配置指南](docs/CONFIG_GUIDE.md)。

## 📖 API 文档

启动服务器后访问：
- Swagger UI: http://localhost:8788/docs
- ReDoc: http://localhost:8788/redoc

## 🧪 测试

```bash
# 运行安装测试
python tests/test_install.py

# 运行示例
python examples/basic_usage.py
```

## 📝 许可证

MIT License

## 🔗 相关项目

- [ReMe](https://github.com/modelscope/agentscope) - 核心记忆管理框架
- [AgentScope](https://github.com/modelscope/agentscope) - 多智能体框架
