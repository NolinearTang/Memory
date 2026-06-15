# 迁移指南 - 平铺结构 → 层次结构

## 📋 变更概览

compress_reme 项目已从**平铺结构**重构为**分层结构**，以提高代码组织性和可维护性。

### 之前（平铺结构）❌
```
compress_reme/
├── __init__.py
├── __main__.py
├── models.py
├── session_manager.py
├── reme_server.py
├── reme_client.py
├── example.py
├── config_example.py
├── test_install.py
├── run_server.sh
├── run_server.bat
├── README.md
├── QUICKSTART.md
├── PROJECT.md
├── CONFIG_GUIDE.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

### 现在（层次结构）✅
```
compress_reme/
├── compress_reme/          # 主代码包
│   ├── core/              # 核心模块
│   ├── server/            # 服务器模块
│   └── client/            # 客户端模块
├── examples/              # 示例代码
├── tests/                 # 测试代码
├── docs/                  # 文档
├── scripts/               # 运行脚本
├── README.md              # 项目概览
├── STRUCTURE.md           # 结构说明
├── MIGRATION.md           # 本文件
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

## 🔄 文件迁移映射表

| 旧位置 | 新位置 | 说明 |
|--------|--------|------|
| `models.py` | `compress_reme/core/models.py` | 数据模型 |
| `session_manager.py` | `compress_reme/core/session_manager.py` | Session管理 |
| `reme_server.py` | `compress_reme/server/app.py` | FastAPI应用 |
| `reme_client.py` | `compress_reme/client/client.py` | Python客户端 |
| `example.py` | `examples/basic_usage.py` | 基础示例 |
| `config_example.py` | `examples/config_example.py` | 配置示例 |
| `test_install.py` | `tests/test_install.py` | 安装测试 |
| `run_server.sh` | `scripts/run_server.sh` | Unix脚本 |
| `run_server.bat` | `scripts/run_server.bat` | Windows脚本 |
| `README.md` | `docs/README.md` | 详细文档 |
| `QUICKSTART.md` | `docs/QUICKSTART.md` | 快速开始 |
| `PROJECT.md` | `docs/PROJECT.md` | 项目概览 |
| `CONFIG_GUIDE.md` | `docs/CONFIG_GUIDE.md` | 配置指南 |
| - | `README.md` | **新**：项目根README |
| - | `STRUCTURE.md` | **新**：结构说明 |
| - | `MIGRATION.md` | **新**：本迁移指南 |

## 📝 代码变更

### 1. 导入路径变更

#### 之前 ❌
```python
# 导入客户端
from compress_reme.reme_client import ReMeClient

# 导入Session管理器
from compress_reme.session_manager import SessionManager

# 导入模型
from compress_reme.models import Message
```

#### 现在 ✅
```python
# 导入客户端
from compress_reme.client import ReMeClient

# 导入Session管理器
from compress_reme.core import SessionManager

# 导入模型
from compress_reme.core.models import Message

# 或者从顶层导入常用类
from compress_reme import ReMeClient, SessionManager, SessionInfo
```

### 2. 服务器启动方式

#### 之前 ❌
```bash
python -m compress_reme.reme_server
```

#### 现在 ✅
```bash
# 方式 1: 使用模块
python -m compress_reme

# 方式 2: 使用命令行工具（如果已安装）
compress-reme-server

# 方式 3: 使用脚本
./scripts/run_server.sh
```

### 3. 示例运行方式

#### 之前 ❌
```bash
python example.py
```

#### 现在 ✅
```bash
# 方式 1: 直接运行
python examples/basic_usage.py

# 方式 2: 使用命令行工具
compress-reme-example
```

## 🔧 配置文件变更

### pyproject.toml

#### 变更 1: 包列表
```toml
# 之前
[tool.setuptools]
packages = ["compress_reme"]

# 现在
[tool.setuptools]
packages = [
    "compress_reme",
    "compress_reme.core",
    "compress_reme.server",
    "compress_reme.client"
]
```

#### 变更 2: 入口点
```toml
# 之前
[project.scripts]
compress-reme-server = "compress_reme.reme_server:main"
compress-reme-client = "compress_reme.reme_client:main"
compress-reme-example = "compress_reme.example:main"

# 现在
[project.scripts]
compress-reme-server = "compress_reme.__main__:main"
compress-reme-client = "compress_reme.client.client:main"
compress-reme-example = "examples.basic_usage:main"
```

## ✅ 迁移步骤（如果你有自定义代码）

### 步骤 1: 更新导入语句

在你的代码中查找并替换：

```bash
# 使用 sed 或手动替换
sed -i 's/from compress_reme.reme_client/from compress_reme.client/g' your_code.py
sed -i 's/from compress_reme.session_manager/from compress_reme.core.session_manager/g' your_code.py
sed -i 's/from compress_reme.models/from compress_reme.core.models/g' your_code.py
```

### 步骤 2: 更新脚本路径

如果你有脚本调用 compress_reme：

```bash
# 之前
python -m compress_reme.reme_server

# 现在
python -m compress_reme
```

### 步骤 3: 重新安装

```bash
# 卸载旧版本（如果已安装）
pip uninstall compress-reme

# 安装新版本
pip install -e .
```

### 步骤 4: 测试

```bash
# 运行测试
python tests/test_install.py

# 运行示例
python examples/basic_usage.py

# 启动服务器测试
python -m compress_reme
```

## 🎯 兼容性说明

### 向后兼容 ✅

以下功能**保持兼容**：

1. **顶层导入**（推荐使用）
   ```python
   from compress_reme import ReMeClient, SessionManager
   ```

2. **API 端点**
   - 所有 HTTP API 端点路径不变
   - 请求/响应格式不变

3. **配置方式**
   - `.env` 文件配置方式不变
   - 环境变量名称不变

4. **功能**
   - 所有功能保持一致
   - 行为无变化

### 需要更新 ⚠️

以下需要**手动更新**：

1. **直接模块导入**
   ```python
   # ❌ 不再支持
   from compress_reme.reme_client import ReMeClient
   
   # ✅ 改为
   from compress_reme.client import ReMeClient
   ```

2. **直接运行模块**
   ```bash
   # ❌ 不再支持
   python -m compress_reme.reme_server
   
   # ✅ 改为
   python -m compress_reme
   ```

3. **文档路径**
   - 详细文档移到 `docs/` 目录
   - 脚本移到 `scripts/` 目录

## 📊 优势对比

| 特性 | 平铺结构 | 层次结构 |
|------|----------|----------|
| **文件组织** | 所有文件混在一起 | 按功能分类清晰 |
| **导航效率** | 需要扫描整个列表 | 直接定位到相关目录 |
| **职责明确** | 不明显 | 一目了然 |
| **扩展性** | 添加文件会更乱 | 添加到相应目录即可 |
| **团队协作** | 容易冲突 | 模块隔离，减少冲突 |
| **可维护性** | 低 | 高 |

## 🔍 常见问题

### Q1: 我的旧代码会报错吗？

**A**: 如果你使用了直接的模块导入（如 `from compress_reme.reme_client import ...`），需要更新导入路径。建议使用顶层导入：`from compress_reme import ReMeClient`。

### Q2: 需要重新安装吗？

**A**: 是的，建议重新安装：
```bash
pip uninstall compress-reme
pip install -e .
```

### Q3: API 会变化吗？

**A**: HTTP API 完全兼容，无任何变化。

### Q4: 文档在哪里？

**A**: 
- 项目概览：根目录 `README.md`
- 详细文档：`docs/` 目录
- 结构说明：`STRUCTURE.md`

### Q5: 之前的示例还能用吗？

**A**: 示例代码移到了 `examples/` 目录，功能完全一致，只需更新运行路径。

## 📞 获取帮助

如果迁移过程中遇到问题：

1. 查看 `STRUCTURE.md` 了解新结构
2. 运行 `python tests/test_install.py` 检查安装
3. 查看 `examples/` 中的示例代码
4. 阅读 `docs/README.md` 详细文档

## 🎉 总结

这次重构带来的好处：

✅ **更清晰的项目结构**  
✅ **更好的代码组织**  
✅ **更容易扩展和维护**  
✅ **更符合Python最佳实践**  
✅ **保持API兼容性**  

欢迎使用新的层次化结构！🚀
