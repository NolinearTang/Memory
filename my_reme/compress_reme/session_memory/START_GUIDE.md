# Session Memory 启动指南

## 🚀 快速启动

### 方式1: 前台启动（推荐用于开发调试）

**直接在终端运行，可以看到实时日志：**

```bash
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme/session_memory

# 使用默认配置启动
python -m __main__

# 或指定端口
python -m __main__ --port 8789

# 或开启自动重载（开发模式）
python -m __main__ --reload

# 或指定所有参数
python -m __main__ --host 0.0.0.0 --port 8789 --log-level info
```

**特点：**
- ✅ 实时查看日志输出
- ✅ Ctrl+C 可以直接停止
- ✅ 适合开发调试
- ❌ 终端关闭服务停止

---

### 方式2: 后台启动（推荐用于生产环境）

**使用 nohup 后台运行：**

```bash
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme/session_memory

# 后台启动，日志输出到 session_memory.log
nohup python -m __main__ --port 8789 > session_memory.log 2>&1 &

# 查看进程ID
echo $!

# 查看日志
tail -f session_memory.log
```

**停止后台服务：**

```bash
# 方法1: 查找进程并杀死
ps aux | grep "__main__"
kill <PID>

# 方法2: 通过端口查找
lsof -ti:8789 | xargs kill

# 方法3: 强制杀死
pkill -f "__main__"
```

**特点：**
- ✅ 终端关闭服务继续运行
- ✅ 适合生产环境
- ✅ 日志保存到文件
- ❌ 需要手动停止

---

### 方式3: Web启动脚本（自动打开浏览器）

**使用提供的启动脚本：**

```bash
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme/session_memory/frontend

# 给脚本执行权限（首次需要）
chmod +x start_web.sh

# 启动服务并打开浏览器
./start_web.sh

# 或指定端口
./start_web.sh 9000
```

**特点：**
- ✅ 自动打开浏览器测试界面
- ✅ 方便测试
- ✅ 前台运行，Ctrl+C停止

---

## 📋 启动参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `--host` | `0.0.0.0` | 监听地址 |
| `--port` | `8789` | 监听端口 |
| `--reload` | `False` | 开启自动重载（开发模式） |
| `--log-level` | `info` | 日志级别 (debug/info/warning/error) |

### 使用示例

```bash
# 只允许本地访问
python -m __main__ --host 127.0.0.1

# 使用9000端口
python -m __main__ --port 9000

# 开发模式（代码修改自动重载）
python -m __main__ --reload

# 详细日志
python -m __main__ --log-level debug

# 组合使用
python -m __main__ --host 0.0.0.0 --port 8080 --reload --log-level debug
```

---

## 🔍 检查服务状态

### 1. 检查服务是否运行

```bash
# 检查端口是否被占用
lsof -i :8789

# 或使用netstat
netstat -an | grep 8789

# 或使用curl测试
curl http://localhost:8789/health
```

### 2. 访问服务

启动成功后，访问以下地址：

- **前端测试页面**: http://localhost:8789/
- **API文档**: http://localhost:8789/docs
- **健康检查**: http://localhost:8789/health

### 3. 查看日志

**前台启动：**直接在终端看到

**后台启动：**
```bash
# 实时查看日志
tail -f session_memory.log

# 查看最后100行
tail -n 100 session_memory.log

# 搜索错误
grep "ERROR" session_memory.log
```

---

## 🛠️ 使用systemd管理（推荐生产环境）

创建systemd服务文件：

```bash
sudo nano /etc/systemd/system/session-memory.service
```

填入以下内容：

```ini
[Unit]
Description=Session Memory Service
After=network.target

[Service]
Type=simple
User=tangshisong
WorkingDirectory=/Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme/session_memory
Environment="LLM_API_KEY=your-api-key"
Environment="LLM_BASE_URL=https://api.openai.com/v1"
ExecStart=/usr/bin/python3 -m __main__ --port 8789
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

管理服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start session-memory

# 停止服务
sudo systemctl stop session-memory

# 重启服务
sudo systemctl restart session-memory

# 查看状态
sudo systemctl status session-memory

# 查看日志
sudo journalctl -u session-memory -f

# 开机自启
sudo systemctl enable session-memory

# 取消开机自启
sudo systemctl disable session-memory
```

---

## 🐳 使用Docker运行（可选）

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8789

CMD ["python", "-m", "__main__", "--host", "0.0.0.0", "--port", "8789"]
```

构建和运行：

```bash
# 构建镜像
docker build -t session-memory .

# 运行容器
docker run -d \
  -p 8789:8789 \
  -e LLM_API_KEY=your-api-key \
  -e LLM_BASE_URL=https://api.openai.com/v1 \
  --name session-memory \
  session-memory

# 查看日志
docker logs -f session-memory

# 停止容器
docker stop session-memory

# 启动容器
docker start session-memory

# 删除容器
docker rm -f session-memory
```

---

## ❌ 常见问题

### 1. 端口被占用

```bash
# 错误信息
OSError: [Errno 48] Address already in use

# 解决方案：查找并杀死占用端口的进程
lsof -ti:8789 | xargs kill -9

# 或使用其他端口
python -m __main__ --port 9000
```

### 2. 模块导入错误

```bash
# 错误信息
ModuleNotFoundError: No module named 'core'

# 解决方案：确保在正确的目录运行
cd /path/to/session_memory
python -m __main__
```

### 3. 权限错误

```bash
# 错误信息
Permission denied

# 解决方案：给脚本执行权限
chmod +x frontend/start_web.sh
```

### 4. API Key未配置

```bash
# 错误信息
必须提供api_key

# 解决方案：配置环境变量
export LLM_API_KEY=your-api-key
export LLM_BASE_URL=https://api.openai.com/v1

# 或编辑 config/config.yml
```

---

## 📊 推荐启动方式

### 开发环境

```bash
# 前台运行 + 自动重载
python -m __main__ --reload --log-level debug
```

### 测试环境

```bash
# 前台运行
python -m __main__ --port 8789
```

### 生产环境

```bash
# 使用systemd或Docker
sudo systemctl start session-memory

# 或使用nohup后台运行
nohup python -m __main__ --port 8789 > session_memory.log 2>&1 &
```

---

## 🎯 快速命令参考

| 场景 | 命令 |
|------|------|
| 前台启动 | `python -m __main__` |
| 后台启动 | `nohup python -m __main__ > session_memory.log 2>&1 &` |
| 停止后台 | `lsof -ti:8789 \| xargs kill` |
| 查看日志 | `tail -f session_memory.log` |
| 检查运行 | `curl http://localhost:8789/health` |
| 开发模式 | `python -m __main__ --reload` |

---

## 📝 完整启动示例

```bash
# 1. 进入项目目录
cd /Users/tangshisong/Library/CloudStorage/OneDrive-个人/inovanceProj/Memory/my_reme/compress_reme/session_memory

# 2. 配置环境变量
export LLM_API_KEY=your-api-key
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4

# 3. 前台启动（开发）
python -m __main__ --reload --log-level debug

# 或后台启动（生产）
nohup python -m __main__ --port 8789 > session_memory.log 2>&1 &
echo $! > session_memory.pid

# 4. 检查服务
curl http://localhost:8789/health

# 5. 访问前端
open http://localhost:8789/

# 6. 停止服务（后台）
kill $(cat session_memory.pid)
```
