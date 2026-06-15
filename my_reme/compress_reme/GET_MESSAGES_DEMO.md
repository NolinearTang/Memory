# get_messages 返回内容说明

## 核心逻辑

`get_messages` **直接返回 `session.messages` 中的所有消息**，返回的是当前状态，而不是原始消息。

```python
# app.py:247
messages = session.messages  # 直接返回当前存储的消息
```

---

## 场景演示

### 场景 1：只添加消息，不压缩

```python
from compress_reme.client import ReMeClient

client = ReMeClient()

# 1. 添加 10 条消息
messages = [
    {"role": "user", "content": "消息1"},
    {"role": "assistant", "content": "回复1"},
    {"role": "user", "content": "消息2"},
    {"role": "assistant", "content": "回复2"},
    {"role": "user", "content": "消息3"},
    {"role": "assistant", "content": "回复3"},
    {"role": "user", "content": "消息4"},
    {"role": "assistant", "content": "回复4"},
    {"role": "user", "content": "消息5"},
    {"role": "assistant", "content": "回复5"},
]

client.add_messages("session_001", messages)

# 2. 获取消息 - ❌ 不压缩
result = client.get_messages("session_001")

print(f"消息数量: {result['total_count']}")
print(f"消息列表:")
for msg in result['messages']:
    print(f"  [{msg['role']}] {msg['content']}")
```

**输出**：

```
消息数量: 10
消息列表:
  [user] 消息1
  [assistant] 回复1
  [user] 消息2
  [assistant] 回复2
  [user] 消息3
  [assistant] 回复3
  [user] 消息4
  [assistant] 回复4
  [user] 消息5
  [assistant] 回复5
```

✅ **所有 10 条消息都在**，完全没有变化。

---

### 场景 2：添加消息后，手动压缩

```python
from compress_reme.client import ReMeClient

client = ReMeClient()

# 1. 添加 10 条消息
messages = [
    {"role": "user", "content": "你好，介绍一下 Python。"},
    {"role": "assistant", "content": "Python 是一种高级编程语言..." * 100},  # 很长的回复
    {"role": "user", "content": "Python 有哪些库？"},
    {"role": "assistant", "content": "常用库包括 NumPy、Pandas..." * 100},  # 很长的回复
    {"role": "user", "content": "如何学习 Python？"},
    {"role": "assistant", "content": "可以从基础语法开始..." * 100},  # 很长的回复
    # ... 更多消息
]

client.add_messages("session_001", messages)

# 2. 查看压缩前
result_before = client.get_messages("session_001")
print(f"压缩前消息数: {result_before['total_count']}")
print(f"压缩前总字符数: {sum(len(m['content']) for m in result_before['messages'])}")

# 3. 手动压缩 ✅
compact_result = client.compact("session_001")
print(f"\n压缩统计:")
print(f"  节省 tokens: {compact_result['tokens_saved']}")
print(f"  压缩比: {compact_result['compression_ratio']:.1%}")

# 4. 查看压缩后
result_after = client.get_messages("session_001")
print(f"\n压缩后消息数: {result_after['total_count']}")
print(f"压缩后总字符数: {sum(len(m['content']) for m in result_after['messages'])}")

print("\n压缩后的消息:")
for msg in result_after['messages']:
    preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
    print(f"  [{msg['role']}] {preview}")
```

**输出示例**：

```
压缩前消息数: 10
压缩前总字符数: 15000

压缩统计:
  节省 tokens: 8000
  压缩比: 53.3%

压缩后消息数: 5
压缩后总字符数: 7000

压缩后的消息:
  [system] 【压缩摘要】前面讨论了 Python 的基础知识和常用库...
  [user] 如何学习 Python？
  [assistant] 可以从基础语法开始...
  [user] 最新的问题
  [assistant] 最新的回复
```

✅ **压缩后的消息**：
- 早期的消息被压缩成了一条系统摘要消息
- 最近的几条消息保留原样
- 消息数量减少了（10 → 5）
- 总字符数减少了（15000 → 7000）

---

## 详细对比

### 情况 A：不压缩

```python
# 添加消息
client.add_messages("session_001", [
    {"role": "user", "content": "消息1"},
    {"role": "assistant", "content": "回复1"},
    {"role": "user", "content": "消息2"},
    {"role": "assistant", "content": "回复2"},
])

# 获取消息
result = client.get_messages("session_001")
```

**返回**：

```json
{
  "session_id": "session_001",
  "total_count": 4,
  "messages": [
    {"name": "user", "role": "user", "content": "消息1", "metadata": {}},
    {"name": "assistant", "role": "assistant", "content": "回复1", "metadata": {}},
    {"name": "user", "role": "user", "content": "消息2", "metadata": {}},
    {"name": "assistant", "role": "assistant", "content": "回复2", "metadata": {}}
  ]
}
```

### 情况 B：压缩后

```python
# 添加消息
client.add_messages("session_001", [
    {"role": "user", "content": "消息1"},
    {"role": "assistant", "content": "回复1" * 1000},  # 很长
    {"role": "user", "content": "消息2"},
    {"role": "assistant", "content": "回复2" * 1000},  # 很长
    {"role": "user", "content": "消息3"},
    {"role": "assistant", "content": "回复3"},
])

# 压缩
client.compact("session_001")

# 获取消息
result = client.get_messages("session_001")
```

**返回**（压缩后）：

```json
{
  "session_id": "session_001",
  "total_count": 3,
  "messages": [
    {
      "name": "system",
      "role": "system",
      "content": "【压缩记忆】之前的对话涉及消息1和消息2，助手提供了详细的回复...",
      "metadata": {"compressed": true, "original_count": 4}
    },
    {"name": "user", "role": "user", "content": "消息3", "metadata": {}},
    {"name": "assistant", "role": "assistant", "content": "回复3", "metadata": {}}
  ]
}
```

✅ **压缩效果**：
- 前 4 条消息 → 1 条压缩摘要
- 最近 2 条消息保持原样
- 总消息数：6 → 3

---

## 实际测试代码

```python
from compress_reme.client import ReMeClient

def demo_without_compact():
    """演示：不压缩的情况"""
    print("=" * 60)
    print("场景 1: 不压缩")
    print("=" * 60)
    
    client = ReMeClient()
    session_id = "demo_no_compact"
    
    # 添加消息
    messages = [
        {"role": "user", "content": f"问题{i}"}
        for i in range(1, 11)
    ] + [
        {"role": "assistant", "content": f"回答{i}" * 100}
        for i in range(1, 11)
    ]
    
    client.add_messages(session_id, messages)
    
    # 获取消息
    result = client.get_messages(session_id)
    
    print(f"消息总数: {result['total_count']}")
    print(f"前 5 条消息:")
    for msg in result['messages'][:5]:
        content_preview = msg['content'][:30] + "..."
        print(f"  [{msg['role']}] {content_preview}")
    
    print("\n✅ 所有消息都保留原样，没有压缩")


def demo_with_compact():
    """演示：压缩后的情况"""
    print("\n" + "=" * 60)
    print("场景 2: 压缩后")
    print("=" * 60)
    
    client = ReMeClient()
    session_id = "demo_with_compact"
    
    # 添加消息
    messages = []
    for i in range(1, 11):
        messages.append({"role": "user", "content": f"问题{i}"})
        messages.append({"role": "assistant", "content": f"这是一个很长的回答{i}..." * 200})
    
    client.add_messages(session_id, messages)
    
    # 查看压缩前
    result_before = client.get_messages(session_id)
    print(f"压缩前消息数: {result_before['total_count']}")
    
    # 压缩
    compact_result = client.compact(session_id, compact_type="memory")
    print(f"\n执行压缩:")
    print(f"  节省 tokens: {compact_result['tokens_saved']:,}")
    print(f"  压缩比: {compact_result['compression_ratio']:.1%}")
    
    # 查看压缩后
    result_after = client.get_messages(session_id)
    print(f"\n压缩后消息数: {result_after['total_count']}")
    print(f"减少了: {result_before['total_count'] - result_after['total_count']} 条消息")
    
    print(f"\n压缩后的消息结构:")
    for i, msg in enumerate(result_after['messages']):
        content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        print(f"  {i+1}. [{msg['role']}] {content_preview}")
    
    print("\n✅ 早期消息被压缩成摘要，最近消息保留原样")


if __name__ == "__main__":
    demo_without_compact()
    demo_with_compact()
```

---

## 关键点总结

### `get_messages` 的行为

```python
# 服务端代码 (app.py:247)
messages = session.messages  # 返回当前状态
```

**不是原始消息，而是当前状态的消息**！

### 三种状态对比

| 操作 | session.messages 的状态 | get_messages 返回 |
|------|------------------------|-------------------|
| **只 add_messages** | 所有原始消息 | 所有原始消息（未压缩） |
| **add + compact** | 部分压缩成摘要 + 最近消息 | 压缩后的消息（减少了） |
| **add + summary** | 所有原始消息（不变） | 所有原始消息 + 可调用 summary 接口获取摘要 |

### 重要区别

**`compact`（压缩）**：
- ✅ 修改 `session.messages`
- ✅ 消息数量会减少
- ✅ 早期消息被压缩成摘要
- ✅ `get_messages` 返回压缩后的消息

**`summary`（摘要）**：
- ❌ **不修改** `session.messages`
- ❌ 消息数量不变
- ✅ 生成一个摘要文本（单独返回）
- ✅ `get_messages` 返回的还是原始消息

---

## 使用建议

### 场景 1：对话历史完整保存（不压缩）

```python
# 适用于：需要完整对话记录的场景
client.add_messages(session_id, messages)
history = client.get_messages(session_id)
# 获取的是完整的原始消息
```

### 场景 2：长对话自动压缩（节省 token）

```python
# 适用于：长对话，需要节省 token 的场景
client.add_messages(session_id, messages)
client.compact(session_id)  # 压缩旧消息
history = client.get_messages(session_id)
# 获取的是压缩后的消息（早期内容变成摘要）
```

### 场景 3：需要摘要但保留原始消息

```python
# 适用于：需要摘要预览，但保留完整历史
client.add_messages(session_id, messages)
summary_result = client.summary(session_id)  # 生成摘要
print(f"摘要: {summary_result['summary']}")

history = client.get_messages(session_id)
# 获取的还是完整的原始消息（不受 summary 影响）
```

---

## 最终答案

**如果不调用 `compact` 和 `summary`**：

```python
client.add_messages("session_001", messages)
result = client.get_messages("session_001")
```

`get_messages` 返回的是：
- ✅ **所有原始消息**，完全没有变化
- ✅ 每条消息都保持添加时的原样
- ✅ 消息数量 = 添加的数量
- ✅ 不会有任何压缩或摘要

**如果调用了 `compact`**：

```python
client.add_messages("session_001", messages)
client.compact("session_001")  # 压缩
result = client.get_messages("session_001")
```

`get_messages` 返回的是：
- ✅ **压缩后的消息**
- ✅ 早期消息被压缩成一条系统摘要
- ✅ 最近的消息保留原样
- ✅ 消息数量减少

**如果调用了 `summary`**：

```python
client.add_messages("session_001", messages)
summary_result = client.summary("session_001")  # 生成摘要
result = client.get_messages("session_001")
```

`get_messages` 返回的是：
- ✅ **所有原始消息**（summary 不修改消息）
- ✅ 摘要单独在 `summary_result['summary']` 中
- ✅ 消息数量不变
