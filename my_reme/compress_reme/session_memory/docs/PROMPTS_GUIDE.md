# Prompts 配置指南

## 概述

所有摘要和压缩的提示词（prompts）都存储在 `prompts.json` 文件中，你可以随时修改这个文件来自定义AI的行为，无需修改代码。

## 配置文件结构

`prompts.json` 包含三个主要部分：

### 1. system_prompts - 系统角色定义

定义AI的身份和基本能力：

```json
{
  "system_prompts": {
    "basic_summary": "你是工控领域的技术专家...",
    "long_answer_compression": "你是工控领域的技术文档压缩专家...",
    "multi_turn_summary": "你是工控领域的资深技术专家..."
  }
}
```

### 2. user_prompts - 用户指令模板

定义具体的任务要求，支持变量替换：

```json
{
  "user_prompts": {
    "basic_summary": {
      "template": "请对以下对话进行摘要：\n{conversation_text}\n要求...",
      "max_chars": 150
    }
  }
}
```

**可用变量：**
- `{conversation_text}` - 完整对话内容
- `{answer}` - 要压缩的回答内容
- `{max_length}` - 目标压缩长度
- `{message_count}` - 消息数量

### 3. llm_parameters - LLM调用参数

控制AI生成的随机性和长度：

```json
{
  "llm_parameters": {
    "basic_summary": {
      "temperature": 0.1,
      "max_tokens": 500
    }
  }
}
```

**参数说明：**
- `temperature`: 0-1之间，越小越严谨稳定，越大越有创造性
- `max_tokens`: 最大生成token数，约等于字数的1.5-2倍

## 三种摘要类型

### 1. basic_summary - 基础摘要

- **使用场景**：少量对话（≤6条消息）的简单摘要
- **默认字数限制**：150字
- **建议temperature**：0.1（严谨）

### 2. long_answer_compression - 长回答压缩

- **使用场景**：assistant回答超过200字时自动压缩
- **默认字数限制**：200字
- **建议temperature**：0.1（保留准确性）

### 3. multi_turn_summary - Session摘要

- **使用场景**：多轮对话（>6条消息）的完整摘要
- **默认字数限制**：1000字
- **建议temperature**：0.1（准确记录技术细节）

## 自定义示例

### 示例1: 修改摘要字数限制

```json
{
  "user_prompts": {
    "multi_turn_summary": {
      "template": "请对以下{message_count}轮工控技术对话进行专业摘要：\n\n{conversation_text}\n\n要求：\n...\n5. 字数限制：不超过500字",
      "max_chars": 500
    }
  },
  "llm_parameters": {
    "multi_turn_summary": {
      "temperature": 0.1,
      "max_tokens": 800
    }
  }
}
```

### 示例2: 修改摘要侧重点

如果你希望更关注解决方案而非诊断过程：

```json
{
  "user_prompts": {
    "multi_turn_summary": {
      "template": "请对以下{message_count}轮工控技术对话进行专业摘要：\n\n{conversation_text}\n\n要求：\n1. 重点提取最终解决方案和操作步骤\n2. 简要描述故障现象\n3. 记录关键参数、设备型号、故障码\n4. 使用专业术语，确保准确性\n5. 字数限制：不超过1000字\n\n技术摘要：",
      "max_chars": 1000
    }
  }
}
```

### 示例3: 调整AI的严谨度

如果希望AI更灵活（不推荐工控领域）：

```json
{
  "llm_parameters": {
    "multi_turn_summary": {
      "temperature": 0.3,
      "max_tokens": 1500
    }
  }
}
```

### 示例4: 自定义工控领域

如果你的领域不是变频器，而是其他设备：

```json
{
  "system_prompts": {
    "multi_turn_summary": "你是工业机器人领域的资深技术专家，擅长机械臂、控制系统、视觉系统的故障诊断和技术支持，能够准确提炼技术对话的核心要点。"
  },
  "user_prompts": {
    "multi_turn_summary": {
      "template": "请对以下{message_count}轮工业机器人技术对话进行专业摘要：\n\n{conversation_text}\n\n要求：\n1. 提取故障现象、诊断过程、解决方案\n2. 记录关键参数、机器人型号、错误代码\n3. 保留技术决策的因果关系\n4. 使用专业术语，确保准确性\n5. 字数限制：不超过1000字\n\n技术摘要：",
      "max_chars": 1000
    }
  }
}
```

## 最佳实践

### ✅ 推荐做法

1. **修改前备份**: 修改前先复制一份 `prompts.json.backup`
2. **逐步调整**: 一次只修改一个参数，测试效果
3. **保持temperature低**: 工控领域建议≤0.2，确保准确性
4. **明确要求**: 在template中明确列出所有要求
5. **合理设置max_tokens**: 约为目标字数的1.5-2倍

### ❌ 避免做法

1. **过高的temperature**: >0.5可能导致输出不稳定
2. **过短的max_chars**: 可能丢失关键信息
3. **过长的max_chars**: 增加成本且可能冗余
4. **删除必要的变量**: 如 `{conversation_text}`

## 如何测试修改

### 1. 修改配置文件

编辑 `prompts.json`：

```bash
nano prompts.json
# 或使用你喜欢的编辑器
```

### 2. 重启服务

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python -m session_memory
```

### 3. 测试效果

使用Web UI或API测试：

```python
# 添加测试对话
response = requests.post("http://localhost:8789/add_message", json={
    "session_id": "test_prompts",
    "messages": [
        {"role": "user", "content": "测试问题"},
        {"role": "assistant", "content": "测试回答..."}
    ],
    "fault_code": [],
    "function_code": [],
    "product_code": []
})

# 等待几秒后查询摘要
time.sleep(3)
result = requests.post("http://localhost:8789/get_message", json={
    "session_id": "test_prompts",
    "query": "测试"
})

print(result.json()["data"]["context"])
```

## 常见问题

### Q: 修改prompts.json后是否需要重启服务？

**A:** 是的，需要重启服务才能加载新的配置。

### Q: 配置文件格式错误会怎样？

**A:** 程序会自动使用内置的默认配置，并在日志中显示警告。

### Q: 可以为不同的session使用不同的prompts吗？

**A:** 当前版本不支持，所有session共用一个prompts.json。如需此功能，可以修改 `ConversationSummarizer` 初始化时传入不同的 `prompts_file` 参数。

### Q: temperature设置多少合适？

**A:** 工控领域建议0.1-0.2之间：
- 0.1: 最严谨，输出稳定一致
- 0.2: 稍有灵活性，但仍然准确
- 0.3+: 可能出现不准确或创造性内容（不推荐）

### Q: max_tokens和max_chars的关系？

**A:** 
- `max_chars`: 提示词中告诉AI的目标字数（中文）
- `max_tokens`: API调用的实际token限制
- 关系：中文约1字=1.5-2 tokens
- 建议：`max_tokens = max_chars * 1.5 ~ 2`

## 高级用法

### 自定义prompts文件路径

```python
from session_memory import ConversationSummarizer

# 使用自定义配置文件
summarizer = ConversationSummarizer(
    prompts_file="/path/to/custom_prompts.json"
)
```

### 在代码中动态修改

```python
# 临时修改配置（不影响文件）
summarizer.prompts_config["llm_parameters"]["multi_turn_summary"]["temperature"] = 0.2
```

## 配置模板

### 模板1: 简洁版（节省成本）

```json
{
  "user_prompts": {
    "multi_turn_summary": {
      "template": "简要摘要以下对话，只保留关键技术点：\n{conversation_text}",
      "max_chars": 500
    }
  },
  "llm_parameters": {
    "multi_turn_summary": {
      "temperature": 0.1,
      "max_tokens": 800
    }
  }
}
```

### 模板2: 详细版（完整记录）

```json
{
  "user_prompts": {
    "multi_turn_summary": {
      "template": "请详细摘要以下对话，包含所有技术细节：\n{conversation_text}\n要求：记录所有操作步骤、参数、结果",
      "max_chars": 2000
    }
  },
  "llm_parameters": {
    "multi_turn_summary": {
      "temperature": 0.05,
      "max_tokens": 3000
    }
  }
}
```

## 支持

如有问题，请查看：
- 服务器日志中的警告信息
- API文档: http://localhost:8789/docs
- 主README: [README.md](README.md)
