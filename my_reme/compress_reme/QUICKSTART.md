# 快速开始指南

## 重要说明

**compress_reme 是一个独立的项目**，工作目录应设置为 compress_reme 文件夹本身。

## 1. 安装依赖

### 方式1: 安装为可编辑包（推荐）

```bash
# 进入 compress_reme 目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme

# 安装 ReMe (依赖)
cd ../../ReMe
pip install -e .

# 回到 compress_reme 并安装
cd ../my_reme/compress_reme
pip install -e .
```

### 方式2: 手动安装依赖

```bash
# 进入 compress_reme 目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme

# 安装 ReMe
cd ../../ReMe
pip install -e .

# 安装其他依赖
cd ../my_reme/compress_reme
pip install -r requirements.txt
```

## 2. 配置环境变量

在 compress_reme 目录创建 `.env` 文件：

```bash
# 进入 compress_reme 目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme

# 复制示例配置
cp ../../ReMe/example.env .env

# 编辑 .env 文件，设置你的 API 密钥
# LLM_API_KEY=your-api-key
# LLM_BASE_URL=https://api.openai.com/v1
```

## 3. 启动服务器

**重要**: 确保当前工作目录是 compress_reme

```bash
# 进入 compress_reme 目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme

# 方式1: 使用便捷脚本（推荐）
./run_server.sh                    # macOS/Linux
run_server.bat                     # Windows

# 方式2: 直接运行模块
python -m compress_reme.reme_server

# 方式3: 指定端口
python -m compress_reme.reme_server --port 8788

# 方式4: 开发模式（自动重载）
python -m compress_reme.reme_server --reload

# 方式5: 如果已安装为包
compress-reme-server                # 从任何目录运行
```

服务器启动后，访问：
- API文档: http://localhost:8788/docs
- 健康检查: http://localhost:8788/health

## 4. 测试客户端

打开新终端，运行：

```bash
# 进入 compress_reme 目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme

# 运行客户端测试
python -m compress_reme.reme_client
# 或直接运行
python reme_client.py

# 运行完整示例
python -m compress_reme.example
# 或直接运行
python example.py

# 如果已安装为包，可以从任何目录运行
compress-reme-client
compress-reme-example
```

## 5. 使用 Python SDK

创建你自己的脚本：

```python
from compress_reme.reme_client import ReMeClient

# 连接服务器
client = ReMeClient("http://localhost:8788")

# 创建会话
session_id = "my_first_session"
client.create_session(session_id)

# 添加消息
messages = [
    {"role": "user", "content": "你好！"},
    {"role": "assistant", "content": "你好！我能帮你什么？"},
]
client.add_messages(session_id, messages)

# 压缩对话
result = client.compact(session_id)
print(f"节省了 {result['tokens_saved']} tokens!")

# 生成摘要
summary = client.summary(session_id)
print(f"摘要: {summary['summary']}")

# 清理
client.delete_session(session_id)
```

## 6. 使用 curl 测试

```bash
# 创建会话
curl -X POST "http://localhost:8788/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "llm_config": {"model_name": "gpt-4o"}
  }'

# 添加消息
curl -X POST "http://localhost:8788/sessions/test_session/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'

# 获取统计
curl "http://localhost:8788/sessions/test_session/stats"

# 删除会话
curl -X DELETE "http://localhost:8788/sessions/test_session"
```

## 故障排除

### 问题1: ModuleNotFoundError: No module named 'reme'

**解决方案**：
```bash
# 安装 ReMe 包
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/ReMe
pip install -e .
```

### 问题2: ModuleNotFoundError: No module named 'compress_reme'

**解决方案**：确保工作目录正确
```bash
# 检查当前目录
pwd
# 应该输出: .../my_reme/compress_reme

# 如果不是，进入正确的目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme
```

### 问题3: 服务器启动失败

**检查端口占用**：
```bash
lsof -i :8788
```

**换个端口**：
```bash
python -m compress_reme.reme_server --port 8800
```

### 问题4: LLM API 错误

**检查环境变量**：
```bash
echo $LLM_API_KEY
echo $LLM_BASE_URL
```

**或在代码中设置**：
```python
import os
os.environ["LLM_API_KEY"] = "your-key"
os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"
```

### 问题5: 连接超时

**增加超时时间**：
```python
client = ReMeClient(timeout=300)  # 5分钟超时
```

## 项目结构说明

```
compress_reme/              # 独立项目根目录（工作目录应设为此处）
├── __init__.py
├── __main__.py
├── models.py
├── session_manager.py
├── reme_server.py         # 服务器
├── reme_client.py         # 客户端
├── example.py             # 示例代码
├── pyproject.toml         # 项目配置
├── requirements.txt       # 依赖列表
├── run_server.sh          # 启动脚本 (Unix)
├── run_server.bat         # 启动脚本 (Windows)
├── README.md              # 完整文档
└── QUICKSTART.md          # 本文件
```

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 查看 [example.py](example.py) 学习更多使用场景
- 访问 http://localhost:8788/docs 查看 API 文档

## 独立运行要点

1. **工作目录**: 始终在 compress_reme 目录下运行
2. **安装**: 可以 `pip install -e .` 安装为可编辑包
3. **脚本**: 使用 `run_server.sh` 或 `run_server.bat` 启动
4. **模块**: 使用 `python -m compress_reme.xxx` 运行模块
5. **直接运行**: 也可以直接 `python reme_server.py` 等
