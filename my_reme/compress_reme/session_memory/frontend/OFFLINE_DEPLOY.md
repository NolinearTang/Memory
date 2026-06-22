# 前端离线部署指南

## ✅ 无外部依赖

经过检查，前端文件**完全无需外部依赖**，可以直接部署到离线环境。

### 前端文件清单

```
frontend/
├── chat.html           # 简单聊天界面（纯HTML+CSS+JS）
├── index.html          # 完整测试界面（纯HTML+CSS+JS）
├── CHAT_GUIDE.md       # 使用说明
├── WEB_UI_GUIDE.md     # 使用说明
└── OFFLINE_DEPLOY.md   # 本文档
```

### 技术栈

- **HTML5** - 页面结构
- **纯CSS3** - 样式和动画（无Bootstrap、Tailwind等）
- **原生JavaScript** - 交互逻辑（无jQuery、React等）
- **Fetch API** - HTTP请求（浏览器原生）
- **LocalStorage** - 会话ID存储（浏览器原生）

### 零外部资源

✅ 无CDN依赖  
✅ 无Google Fonts  
✅ 无Font Awesome  
✅ 无图片资源  
✅ 无第三方库  

## 📦 离线部署步骤

### 方式1: 通过后端部署（推荐）

```bash
# 1. 复制整个项目到离线服务器
scp -r session_memory/ user@offline-server:/path/to/

# 2. 在离线服务器上启动
cd /path/to/session_memory
python -m __main__

# 3. 访问（局域网内任何设备）
http://离线服务器IP:8789/chat-ui
http://离线服务器IP:8789/web
```

### 方式2: 独立部署（如需）

如果需要将前端放到独立的Web服务器：

```bash
# 1. 复制前端文件
cp frontend/chat.html /var/www/html/
cp frontend/index.html /var/www/html/

# 2. 修改API地址（编辑HTML文件）
# chat.html 第236行
const API_BASE_URL = 'http://后端服务器IP:8789';

# index.html 第335行
<input type="text" id="apiUrl" value="http://后端服务器IP:8789">

# 3. 访问前端
http://前端服务器IP/chat.html
http://前端服务器IP/index.html
```

## 🔧 配置修改

### 修改API地址

#### chat.html

```javascript
// 第236行
const API_BASE_URL = 'http://localhost:8789';  // 改为实际地址
```

#### index.html

```html
<!-- 第335行 -->
<input type="text" id="apiUrl" value="http://localhost:8789">  <!-- 改为实际地址 -->
```

## 🌐 网络配置

### 防火墙规则

```bash
# 允许8789端口（后端API）
firewall-cmd --permanent --add-port=8789/tcp
firewall-cmd --reload

# 或使用iptables
iptables -A INPUT -p tcp --dport 8789 -j ACCEPT
```

### Nginx反向代理（可选）

如果希望通过80端口访问：

```nginx
# /etc/nginx/conf.d/session-memory.conf
server {
    listen 80;
    server_name session-memory.local;

    # 前端页面
    location / {
        proxy_pass http://localhost:8789;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API请求
    location /chat {
        proxy_pass http://localhost:8789/chat;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

然后访问：
```
http://session-memory.local/chat-ui
http://session-memory.local/web
```

## 📱 支持的浏览器

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ 国产浏览器（基于Chromium内核）

### 浏览器要求

- 支持 ES6+ (const, let, arrow functions)
- 支持 Fetch API
- 支持 LocalStorage
- 支持 CSS Grid/Flexbox

**所有现代浏览器都满足要求，无需额外配置。**

## 🧪 离线测试

### 1. 测试前端文件

```bash
# 在离线环境打开HTML文件
chromium-browser --disable-web-security frontend/chat.html

# 或使用Python启动简单HTTP服务器
cd frontend
python -m http.server 8080
# 访问 http://localhost:8080/chat.html
```

### 2. 测试API连接

```bash
# 在前端界面点击"测试连接"按钮
# 或使用curl测试
curl http://后端IP:8789/health
```

### 3. 完整测试

```bash
# 1. 启动后端
python -m __main__

# 2. 浏览器访问
http://localhost:8789/chat-ui

# 3. 输入测试消息
"你好" -> 应收到AI回复

# 4. 检查session保存
ls -la .session_memory/messages/
```

## 🔒 安全建议

### 离线环境安全措施

1. **修改默认端口**
```yaml
# config/config.yml
server:
  port: 18789  # 改为非标准端口
```

2. **限制访问IP**
```yaml
server:
  host: "192.168.1.0"  # 只监听特定网段
```

3. **添加认证（如需）**

可以在Nginx层添加基本认证：
```nginx
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8789;
}
```

## 📊 性能优化

### 前端优化

前端已经是最优状态：
- ✅ 零依赖，加载速度快
- ✅ CSS内联，无额外请求
- ✅ 代码简洁，体积小（~12KB + ~21KB）

### 后端优化

```yaml
# config/config.yml
session:
  keep_recent: 2              # 减少内存占用
  compress_threshold: 150     # 更积极压缩
  max_turns_before_summary: 4 # 更快生成摘要
```

## 🐛 常见问题

### Q: 前端显示"无法连接到服务"

**A:** 检查：
1. 后端是否启动：`curl http://localhost:8789/health`
2. 防火墙是否开放：`firewall-cmd --list-ports`
3. API地址是否正确：查看浏览器控制台（F12）

### Q: 跨域问题（CORS）

**A:** 后端已配置CORS，允许所有来源：
```python
# app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

如果还有问题，检查Nginx配置。

### Q: 前端无法保存session_id

**A:** 确保浏览器允许LocalStorage：
- 不要使用"隐私模式"
- 检查浏览器设置中"网站数据"权限

## 📝 总结

### 部署检查清单

- [ ] 复制项目文件到离线服务器
- [ ] 修改config/config.yml中的配置
- [ ] 修改前端API地址（如需独立部署）
- [ ] 开放防火墙端口
- [ ] 启动后端服务
- [ ] 测试前端访问
- [ ] 测试API连接
- [ ] 测试完整对话流程

### 最简部署

```bash
# 三步完成
1. 启动: python -m __main__
2. 访问: http://服务器IP:8789/chat-ui
3. 测试: 发送消息
```

✅ **前端完全无外部依赖，可直接部署到任何离线环境！**
