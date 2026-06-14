# Compress ReMe 项目概览

## 项目定位

**compress_reme** 是一个基于 ReMe 的独立项目，提供 Session 级别的对话压缩和记忆抽取服务。

## 核心特点

1. **独立项目** - 不依赖于父目录，可单独运行和部署
2. **不修改 ReMe** - 完全通过组合和封装实现功能
3. **工作目录** - 以 `compress_reme` 文件夹作为工程根目录
4. **Server-Client 架构** - 提供 HTTP API 和 Python SDK

## 项目结构

```
compress_reme/                    # 项目根目录（工作目录）
├── __init__.py                   # 包初始化，导出公共接口
├── __main__.py                   # 支持 python -m 运行
├── models.py                     # Pydantic 数据模型定义
├── session_manager.py            # Session 管理器
├── reme_server.py                # FastAPI 服务器
├── reme_client.py                # Python 客户端 SDK
├── example.py                    # 使用示例
├── test_install.py               # 安装测试脚本
│
├── pyproject.toml                # 项目配置（支持 pip install）
├── requirements.txt              # 依赖列表
│
├── run_server.sh                 # 启动脚本 (Unix)
├── run_server.bat                # 启动脚本 (Windows)
│
├── README.md                     # 完整文档
├── QUICKSTART.md                 # 快速开始
├── PROJECT.md                    # 本文件
└── .gitignore                    # Git 忽略规则
```

## 核心模块说明

### 1. models.py
定义所有 API 的请求和响应模型：
- `CreateSessionRequest/Response`
- `AddMessagesRequest/Response`
- `CompactRequest/Response`
- `SummaryRequest/Response`
- `SearchRequest/Response`
- 等等...

### 2. session_manager.py
管理多个 ReMeLight 实例：
- `SessionInfo` - Session 信息类
- `SessionManager` - Session 生命周期管理
  - 创建/删除 session
  - Session 统计
  - 自动清理不活跃 session

### 3. reme_server.py
FastAPI 服务器，提供 RESTful API：
- Session 管理接口
- 消息管理接口
- 对话压缩接口
- 摘要生成接口
- 记忆搜索接口
- 统计信息接口

### 4. reme_client.py
Python 客户端 SDK：
- `ReMeClient` 类封装所有 API 调用
- 提供简洁的 Python 接口
- 自动处理请求/响应

### 5. example.py
6 个实用示例：
- 基础工作流
- 长对话压缩
- 摘要生成
- 记忆搜索
- 多会话管理
- Tool 结果压缩

## 运行方式

### 作为独立项目运行（推荐）

```bash
# 1. 进入项目目录
cd compress_reme

# 2. 安装依赖
pip install -e .

# 3. 启动服务器
./run_server.sh              # 或 python -m compress_reme.reme_server

# 4. 运行示例
python example.py
```

### 作为 Python 包使用

安装后可在任何位置使用：

```bash
# 启动服务器
compress-reme-server

# 运行客户端测试
compress-reme-client

# 运行示例
compress-reme-example
```

### 直接运行脚本

```bash
cd compress_reme

# 直接运行服务器
python reme_server.py

# 直接运行客户端测试
python reme_client.py

# 直接运行示例
python example.py
```

## 技术栈

- **Web 框架**: FastAPI - 高性能异步框架
- **ASGI 服务器**: Uvicorn - 支持异步
- **数据验证**: Pydantic - 类型安全
- **HTTP 客户端**: Requests - 简洁易用
- **核心引擎**: ReMe (ReMeLight) - 对话压缩和记忆管理
- **LLM 框架**: AgentScope - 多智能体框架

## 与 ReMe 的关系

### 依赖关系
- **依赖 ReMe**：使用 ReMe 的 ReMeLight 类
- **不修改 ReMe**：完全通过导入和调用实现
- **独立部署**：可单独安装和运行

### 功能扩展
compress_reme 在 ReMe 基础上增加：
1. **Session 管理** - 多会话隔离
2. **HTTP API** - RESTful 接口
3. **统计功能** - 使用统计和监控
4. **批量操作** - 批量会话管理
5. **客户端 SDK** - 简化调用

### 设计原则
- **组合优于继承** - 使用 ReMeLight 实例
- **封装不侵入** - 不修改 ReMe 源码
- **独立可部署** - 完整的项目结构

## 部署方案

### 开发环境

```bash
cd compress_reme
pip install -e .
python -m compress_reme.reme_server --reload
```

### 生产环境

```bash
# 安装
cd compress_reme
pip install .

# 使用 systemd (Linux)
sudo systemctl start compress-reme

# 使用 Docker
docker build -t compress-reme .
docker run -p 8788:8788 compress-reme
```

### 云部署

支持部署到：
- AWS Lambda + API Gateway
- Google Cloud Run
- Azure Container Instances
- 任何支持 Python 的云平台

## API 设计

### RESTful 风格
- `GET /sessions` - 列出会话
- `POST /sessions` - 创建会话
- `DELETE /sessions/{id}` - 删除会话
- `POST /sessions/{id}/messages` - 添加消息
- `POST /sessions/{id}/compact` - 压缩对话
- `POST /sessions/{id}/summary` - 生成摘要
- `POST /sessions/{id}/search` - 搜索记忆

### 响应格式
统一 JSON 格式，包含：
- 数据字段
- 状态信息
- 时间戳

### 错误处理
- HTTP 状态码标准
- 详细错误信息
- 友好错误提示

## 测试策略

### 单元测试
```bash
pytest tests/
```

### 集成测试
```bash
python test_install.py
python -m compress_reme.reme_client
```

### 完整测试
```bash
python -m compress_reme.example
```

## 性能考虑

- **异步架构** - FastAPI + Uvicorn
- **Session 隔离** - 每个 session 独立实例
- **自动清理** - 清理不活跃 session
- **连接池** - HTTP 客户端连接复用

## 安全考虑

- **API 认证** - 可添加 Token 验证
- **HTTPS** - 生产环境使用 HTTPS
- **输入验证** - Pydantic 自动验证
- **环境变量** - 敏感信息使用 .env

## 扩展方向

1. **认证授权** - 添加用户认证
2. **持久化** - Session 数据持久化
3. **分布式** - 支持多实例部署
4. **监控告警** - 集成 Prometheus/Grafana
5. **WebSocket** - 实时通信支持

## 维护指南

### 更新依赖
```bash
pip install --upgrade -r requirements.txt
```

### 代码格式化
```bash
black .
flake8 .
```

### 生成文档
```bash
# API 文档自动生成（访问 /docs）
# Markdown 文档手动维护
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 发起 Pull Request

## 许可证

MIT License

## 联系方式

- GitHub Issues: 提交问题
- Documentation: 查看 README.md
- Examples: 查看 example.py

---

**最后更新**: 2026-06-13
**版本**: 1.0.0
**状态**: ✅ 稳定
