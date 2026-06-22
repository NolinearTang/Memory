# 调试工具使用指南

## 🔍 查看Session数据流

本项目提供了多种方式来查看 `get_message` 返回的数据和送给LLM的数据。

## 工具1: 调试端点 `/debug/context`

### API调用

```bash
# 查看指定session的上下文数据
curl -X POST http://localhost:8789/debug/context \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_1782132943177_2xeig0qhc",
    "query": "散热"
  }'
```

### 返回示例

```json
{
  "session_id": "session_1782132943177_2xeig0qhc",
  "query": "散热",
  "get_message_result": {
    "code": 200,
    "message": "success",
    "data": {
      "session_id": "session_1782132943177_2xeig0qhc",
      "state": "产品信息: MD500, 故障码: E001",
      "context": "对话摘要: 讨论MD500变频器E001过热报警问题\n\n近期对话:\n[user]: MD500显示E001报警\n[assistant]: E001是过热保护报警...\n\n相关对话:\n- [user]: 如何散热？\n- [assistant]: 散热方法包括..."
    }
  },
  "context_length": 256,
  "will_use_context": true,
  "llm_input": {
    "model": "qwen3.6-35b-a3b",
    "system_prompt": "你是一个友好、专业的AI助手...",
    "user_input": "=== 上下文信息 ===\n对话摘要: ...\n\n=== 当前问题 ===\n散热",
    "user_input_length": 280
  }
}
```

### 关键字段说明

- `get_message_result.data.context` - 这就是从 `get_message()` 获取的上下文字符串
- `get_message_result.data.state` - 产品信息、故障码等状态
- `llm_input.system_prompt` - 送给LLM的系统提示词
- `llm_input.user_input` - 送给LLM的用户输入（包含上下文）

## 工具2: Python调试脚本

### 交互模式

```bash
# 启动交互式调试
python debug_session.py

# 输出:
📋 所有Session:
  1. session_1782132943177_2xeig0qhc
  2. default_session

请选择要调试的session（输入序号）:
序号: 1

选中Session: session_1782132943177_2xeig0qhc
输入查询内容（直接回车跳过）: 散热

# 然后会显示完整的调试信息
```

### 命令行模式

```bash
# 直接调试指定session
python debug_session.py session_1782132943177_2xeig0qhc "散热"

# 输出示例:
================================================================================
📊 Session数据调试
Session ID: session_1782132943177_2xeig0qhc
Query: 散热
================================================================================

📋 基本信息:
  Session ID: session_1782132943177_2xeig0qhc
  Query: 散热
  是否有上下文: ✅ 是
  上下文长度: 256 字符

================================================================================
📦 get_message() 返回的数据:
================================================================================

Code: 200
Message: success

📌 State信息:
  产品信息: MD500, 故障码: E001

📝 Context信息:
--------------------------------------------------------------------------------
对话摘要: 讨论MD500变频器E001过热报警问题及解决方案

近期对话:
[user]: MD500显示E001报警
[assistant]: E001是过热保护报警，可能原因包括：1) 环境温度过高...
[user]: 如何改善散热？
[assistant]: 改善散热的方法：1) 增加通风...

相关对话:
- [user]: E001具体是什么意思？
- [assistant]: E001代表变频器内部温度超过安全阈值...
--------------------------------------------------------------------------------

================================================================================
🤖 送给LLM的数据:
================================================================================

模型: qwen3.6-35b-a3b
用户输入长度: 280 字符

--- System Prompt ---
你是一个友好、专业的AI助手。
重要提示：用户的问题基于之前的对话上下文。请仔细阅读提供的上下文信息...

--- User Input ---
=== 上下文信息 ===
对话摘要: 讨论MD500变频器E001过热报警问题及解决方案

近期对话:
[user]: MD500显示E001报警
[assistant]: E001是过热保护报警...

=== 当前问题 ===
散热
```

## 工具3: 查看原始文件

### 查看元数据文件

```bash
# 使用jq格式化JSON
cat .session_memory/metadata/session_xxx.json | jq

# 不使用jq（原始JSON）
cat .session_memory/metadata/session_xxx.json

# 输出示例:
{
  "session_id": "session_1782132943177_2xeig0qhc",
  "fault_code": ["E001"],
  "function_code": [],
  "product_code": ["MD500"],
  "session_summary": "讨论了MD500变频器E001过热报警问题及解决方案",
  "all_messages": [
    {
      "role": "user",
      "content": "MD500显示E001报警"
    },
    {
      "role": "assistant",
      "content": "E001是过热保护报警，可能原因包括..."
    }
  ],
  "recent_messages": [
    {
      "role": "user",
      "content": "如何改善散热？"
    },
    {
      "role": "assistant",
      "content": "改善散热的方法：1) 增加通风...",
      "original_length": 350
    }
  ],
  "message_summaries": {
    "0": "讨论了E001报警的含义和原因"
  }
}
```

### 查看消息历史

```bash
# 查看完整消息历史（JSONL格式）
cat .session_memory/messages/session_xxx.jsonl

# 格式化每一行
cat .session_memory/messages/session_xxx.jsonl | while read line; do echo "$line" | jq; done

# 输出示例:
{"role": "user", "content": "MD500显示E001报警"}
{"role": "assistant", "content": "E001是过热保护报警..."}
{"role": "user", "content": "如何改善散热？"}
{"role": "assistant", "content": "改善散热的方法..."}
```

## 工具4: 实时日志

### 启用调试日志

```bash
# 启动时查看详细日志
python -m __main__

# 日志示例:
2026-06-22 21:03:32 - app - INFO - [session_xxx] 收到聊天请求: 散热...
2026-06-22 21:03:32 - app - INFO - [session_xxx] 获取到上下文，长度: 256
2026-06-22 21:03:32 - app - DEBUG - [session_xxx] 上下文内容: 对话摘要: 讨论MD500...
2026-06-22 21:03:32 - app - INFO - [session_xxx] 使用上下文回答
2026-06-22 21:03:35 - app - INFO - [session_xxx] LLM回复: 散热改善建议...
2026-06-22 21:03:35 - app - INFO - [session_xxx] 对话已保存
```

### 启用DEBUG级别日志

编辑 `config/config.yml`:

```yaml
server:
  log_level: "debug"  # 从 "info" 改为 "debug"
```

重启后会看到更详细的日志，包括上下文内容预览。

## 📊 数据对比

### get_message() 返回的数据

```python
{
  "code": 200,
  "data": {
    "context": "对话摘要: ...\n\n近期对话:\n...\n\n相关对话:\n..."
  }
}
```

**关键点：**
- `data.context` 是已经格式化好的字符串
- 包含：对话摘要 + 近期对话 + BM25检索的相关对话
- 这个字符串会直接拼接到用户问题前面

### 送给LLM的数据

```python
{
  "model_name": "qwen3.6-35b-a3b",
  "prompt": "你是一个友好、专业的AI助手...",
  "content": "=== 上下文信息 ===\n{context}\n\n=== 当前问题 ===\n{user_question}",
  "max_tokens": 1024
}
```

**关键点：**
- `prompt` 是系统提示词
- `content` 包含完整的上下文 + 当前问题
- 使用 `===` 分隔符清晰标记上下文和问题

## 🎯 调试场景

### 场景1: 验证上下文是否获取

```bash
# 使用调试端点
curl -X POST http://localhost:8789/debug/context \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_xxx", "query": ""}' | jq '.context_length'

# 如果返回 > 0，说明有上下文
```

### 场景2: 查看具体上下文内容

```bash
# 使用Python脚本（推荐）
python debug_session.py session_xxx

# 或查看日志（启动时设置log_level: debug）
```

### 场景3: 对比模型输入输出

```bash
# 1. 查看送给LLM的输入
python debug_session.py session_xxx "测试问题"

# 2. 实际调用/chat，查看日志
curl -X POST http://localhost:8789/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "测试问题", "session_id": "session_xxx"}'

# 3. 对比日志中的输入和输出
```

## 📝 配置说明

详细配置说明请查看：[SESSION_CONFIG_GUIDE.md](SESSION_CONFIG_GUIDE.md)

关键配置：
- `keep_recent: 3` - 保留最近3轮对话
- `compress_threshold: 200` - 超过200字压缩
- `max_turns_before_summary: 6` - 6条消息后生成详细摘要

## 🚀 快速调试流程

```bash
# 1. 列出所有session
curl http://localhost:8789/sessions

# 2. 查看具体session的数据
python debug_session.py <session_id>

# 3. 查看原始文件
cat .session_memory/metadata/<session_id>.json | jq

# 4. 测试查询
curl -X POST http://localhost:8789/debug/context \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session_id>", "query": "测试"}'
```

## 💡 提示

1. **首次对话** - 没有上下文，`context_length` 为 0
2. **第二轮开始** - 会获取到上下文，包含之前的对话
3. **上下文来源** - 对话摘要 + 近期对话 + BM25检索相关对话
4. **压缩机制** - 长回答会被压缩，保留 `original_length` 字段
5. **摘要生成** - 异步生成，可能延迟几秒

查看完整数据流请参考：[SESSION_CONFIG_GUIDE.md](SESSION_CONFIG_GUIDE.md)
