# Session 配置说明和数据流分析

## 📋 配置参数详解

### session 配置项

```yaml
session:
  keep_recent: 3              # 保留最近N轮对话
  compress_threshold: 200     # 长回答压缩阈值（字符数）
  max_turns_before_summary: 6 # 超过此消息数启用详细摘要
```

### 1. keep_recent: 3

**含义：** 在元数据中保留最近3轮（6条消息）的完整对话

**工作逻辑：**
```
完整消息历史（all_messages）:
  [消息1, 消息2, 消息3, 消息4, 消息5, 消息6, 消息7, 消息8]

keep_recent = 3，保留最近3轮 = 6条消息:
  recent_messages = [消息3, 消息4, 消息5, 消息6, 消息7, 消息8]
  
旧消息会被摘要压缩，不直接保存在 recent_messages 中
```

**代码实现：**
```python
# core/session_manager.py
session_config = config.get('session', {})
keep_recent = session_config.get('keep_recent', 3)

# 计算要保留的消息数（每轮=2条消息：user+assistant）
keep_count = keep_recent * 2
recent_messages = all_messages[-keep_count:] if len(all_messages) > keep_count else all_messages
```

**作用：**
- 快速访问最近对话，无需读取完整历史
- 控制元数据文件大小
- 旧对话通过摘要保存，节省存储

### 2. compress_threshold: 200

**含义：** 如果助手回答超过200个字符，会被压缩

**工作逻辑：**
```
助手回答: "这是一个很长的回答..." (350个字符)

如果 len(回答) > 200:
    调用 LLM 压缩 -> "简短总结..." (150个字符)
    保存: {
        "role": "assistant",
        "content": "简短总结...",
        "original_length": 350  # 记录原始长度
    }
```

**代码实现：**
```python
# core/session_manager.py
compress_threshold = session_config.get('compress_threshold', 200)

for msg in recent_messages:
    content = msg.get("content", "")
    if msg["role"] == "assistant" and len(content) > compress_threshold:
        # 压缩长回答
        compressed = await self.summarizer.compress_long_answer(
            content, 
            max_length=compress_threshold
        )
```

**作用：**
- 减少token消耗（传给LLM时更短）
- 保持核心信息，去除冗余
- 适合长篇技术解释

### 3. max_turns_before_summary: 6

**含义：** 当消息数超过6条时，使用详细摘要；否则使用基础摘要

**工作逻辑：**
```
消息历史 = [消息1, 消息2, 消息3, 消息4]  # 4条消息（2轮）

if len(消息) <= 6:
    使用 "basic_summary" prompt  # 简短摘要
else:
    使用 "multi_turn_summary" prompt  # 详细摘要，包含更多上下文
```

**代码实现：**
```python
# core/summarizer.py
async def summarize_multiple_turns(self, messages, max_turns=6):
    if len(messages) <= max_turns:
        prompt_key = "basic_summary"        # 简短版
    else:
        prompt_key = "multi_turn_summary"   # 详细版
```

**作用：**
- 短对话：生成简短摘要，节省token
- 长对话：生成详细摘要，保留更多信息
- 自动适应对话长度

## 🔍 数据流分析

### 数据流程图

```
用户输入 "如何解决E001？"
    ↓
前端发送: {"message": "如何解决E001？", "session_id": "session_xxx"}
    ↓
后端 /chat API
    ↓
1. 调用 manager.get_message(session_id, query, top_k=3)
    ↓
2. get_message 返回:
   {
     "code": 200,
     "data": {
       "context": "对话摘要: MD500变频器E001报警问题\n\n近期对话:\n[user]: E001是什么？\n[assistant]: E001是过热保护...",
       "state": "产品信息: MD500, 故障码: E001"
     }
   }
    ↓
3. 构造输入给LLM:
   System: "你是AI助手，请基于上下文回答..."
   User: "=== 上下文信息 ===\n{context}\n\n=== 当前问题 ===\n如何解决E001？"
    ↓
4. LLM返回: "针对E001过热报警，建议..."
    ↓
5. 保存对话: manager.add_message(session_id, [user_msg, assistant_msg])
    ↓
6. 返回给前端: {"reply": "针对E001...", "usage": {}}
```

### get_message 返回的数据示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "session_1782132943177_2xeig0qhc",
    "state": "产品信息: MD500, 故障码: E001",
    "context": "对话摘要: 讨论MD500变频器E001过热报警问题及解决方案\n\n近期对话:\n[user]: MD500显示E001报警\n[assistant]: E001是过热保护报警，可能原因包括：1) 环境温度过高 2) 散热风扇故障...\n[user]: 如何改善散热？\n[assistant]: 改善散热的方法：1) 增加通风 2) 清理灰尘...\n\n相关对话:\n- [user]: E001具体是什么意思？\n- [assistant]: E001代表变频器内部温度超过安全阈值..."
  }
}
```

### 送到LLM的数据示例

**有上下文时：**

```
Model: qwen3.6-35b-a3b

System Prompt:
"你是一个友好、专业的AI助手。
重要提示：用户的问题基于之前的对话上下文。请仔细阅读提供的上下文信息（包括对话摘要、近期对话和相关历史对话），并基于这些上下文来理解和回答当前问题。
如果用户的问题中有代词（如"它"、"这个"等），请根据上下文判断其具体指代。
请用简洁、准确的语言回答用户的问题。"

User Input:
"=== 上下文信息 ===
对话摘要: 讨论MD500变频器E001过热报警问题及解决方案

近期对话:
[user]: MD500显示E001报警
[assistant]: E001是过热保护报警，可能原因包括：1) 环境温度过高 2) 散热风扇故障...
[user]: 如何改善散热？
[assistant]: 改善散热的方法：1) 增加通风 2) 清理灰尘...

相关对话:
- [user]: E001具体是什么意思？
- [assistant]: E001代表变频器内部温度超过安全阈值...

=== 当前问题 ===
还有其他建议吗？"

Temperature: 0.01
Max Tokens: 1024
```

**无上下文时（首次对话）：**

```
Model: qwen3.6-35b-a3b

System Prompt:
"你是一个友好、专业的AI助手。请用简洁、准确的语言回答用户的问题。"

User Input:
"MD500变频器显示E001报警"

Temperature: 0.01
Max Tokens: 1024
```

## 🛠️ 调试工具

### 查看实际数据

使用新增的调试端点：

```bash
# 1. 进行几轮对话后，查看session上下文
curl -X POST http://localhost:8789/debug/context \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_xxx",
    "query": "散热"
  }'

# 返回:
{
  "session_id": "session_xxx",
  "get_message_result": {
    "code": 200,
    "data": {
      "context": "...",
      "state": "..."
    }
  },
  "context_length": 256,
  "will_use_context": true
}
```

### 查看完整session数据

```bash
# 查看session元数据文件
cat .session_memory/metadata/session_xxx.json | jq

# 输出示例:
{
  "session_id": "session_xxx",
  "fault_code": ["E001"],
  "function_code": [],
  "product_code": ["MD500"],
  "session_summary": "讨论MD500变频器E001过热报警...",
  "all_messages": [
    {"role": "user", "content": "MD500显示E001报警"},
    {"role": "assistant", "content": "E001是过热保护..."}
  ],
  "recent_messages": [
    {"role": "user", "content": "如何改善散热？"},
    {"role": "assistant", "content": "改善散热方法：1) 增加通风...", "original_length": 350}
  ],
  "message_summaries": {
    "0": "讨论了E001报警的含义和原因"
  }
}
```

## 📊 完整示例

### 配置

```yaml
session:
  keep_recent: 3              # 保留6条消息
  compress_threshold: 200     # 超过200字压缩
  max_turns_before_summary: 6 # 6条消息内用简短摘要
```

### 对话过程

**第1轮：**
```
User: "MD500变频器显示E001报警"
Assistant: "E001是过热保护报警，原因可能有..." (120字)

数据变化:
- all_messages: 2条
- recent_messages: 2条（未压缩，因为<200字）
- session_summary: 空（消息数<=6，暂不生成摘要）
```

**第2轮：**
```
User: "如何解决？"
Assistant: "解决E001报警的方法包括：1) 检查环境温度..." (280字)

数据变化:
- all_messages: 4条
- recent_messages: 4条（assistant回答被压缩到200字）
- session_summary: 空
```

**第4轮（第8条消息）：**
```
User: "还有其他建议吗？"

数据变化:
- all_messages: 8条
- recent_messages: 6条（keep_recent=3轮=6条）
- session_summary: "讨论了MD500变频器E001过热报警..." 
  （消息数>6，生成详细摘要）
```

## 🎯 调优建议

### 根据使用场景调整

**技术支持（推荐）：**
```yaml
session:
  keep_recent: 3              # 足够上下文
  compress_threshold: 200     # 技术回答通常较长
  max_turns_before_summary: 6 # 适中
```

**快速问答：**
```yaml
session:
  keep_recent: 2              # 更少历史
  compress_threshold: 150     # 更短回答
  max_turns_before_summary: 4 # 更快生成摘要
```

**深度对话：**
```yaml
session:
  keep_recent: 5              # 更多历史
  compress_threshold: 300     # 保留详细信息
  max_turns_before_summary: 10 # 延迟摘要
```

## 📝 总结

- **keep_recent**: 控制元数据保留多少轮对话（2条消息=1轮）
- **compress_threshold**: 长回答自动压缩，节省token
- **max_turns_before_summary**: 短对话简短摘要，长对话详细摘要

数据流：用户输入 → 获取上下文 → 构造prompt → LLM生成 → 保存对话 → 异步摘要/压缩
