"""
问题改写模块 - 基于上下文改写用户问题（面向ES全文检索优化）

职责：
1. 从input_message获取上下文
2. 判断首轮/次轮对话
3. 调用LLM改写问题为适合ES检索的表述
4. 返回改写后的问题

改写策略（针对ES + ik分词器）：
- 补充产品型号，放在句首
- 保留所有关键技术词（故障码、功能码、参数名等）
- 使用规范术语（变频器、报警、功能码等）
- 关键词适当分隔，便于分词匹配
- 去掉无意义的口语词和助词

注意：
- context由外部传入（session.get()的结果）
- codes提取和标准化由后续的实体检测层处理
"""

from typing import Dict, Any, Optional
from core.llm_client import LlmClient
from config.config import get_config


class QueryRewriter:
    """问题改写器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化改写器
        
        Args:
            config: 配置字典
        """
        self.llm_client = LlmClient(config)
        self.model_name = config.get('llm', {}).get('selected_model', 'gpt4')
    
    async def rewrite(self, input_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        改写问题
        
        Args:
            input_message: {
                "query": "用户问题",
                "context": {  # session.get() 返回的上下文
                    "context": "上下文内容",
                    "messages": [...],
                    ...
                },
                "envs": {
                    "product": "MD630"  # 可选，默认产品
                }
            }
        
        Returns:
            {
                "rewritten_query": "改写后的问题"
            }
        """
        # 1. 提取输入信息
        query = input_message.get("query", "")
        context_result = input_message.get("context", {})
        default_product = input_message.get("envs", {}).get("product", "")
        
        # 2. 判断是否首轮对话
        is_first_turn = self._is_first_turn(context_result)
        
        # 3. 调用LLM改写
        if is_first_turn:
            rewritten = await self._rewrite_first_turn(query, default_product)
        else:
            context = context_result.get('context', '')
            rewritten = await self._rewrite_multi_turn(query, context)
        
        return {
            "rewritten_query": rewritten
        }
    
    def _is_first_turn(self, context_result: Dict[str, Any]) -> bool:
        """判断是否首轮对话"""
        if 'error' in context_result:
            return True
        
        messages = context_result.get('messages', [])
        context = context_result.get('context', '')
        
        # 如果没有消息或上下文为空，认为是首轮
        return len(messages) == 0 or not context.strip()
    
    async def _rewrite_first_turn(
        self, 
        query: str, 
        default_product: str
    ) -> str:
        """
        首轮对话改写
        
        重点：将用户问题改写为适合ES全文检索的表述（ik分词器优化）
        """
        # 构建提示信息
        product_hint = f"（默认产品：{default_product}）" if default_product else ""
        
        prompt = f"""你是一个变频器技术支持助手。请将用户问题改写为适合Elasticsearch全文检索的表述。

**用户问题**：{query}
{product_hint}

**改写要求**（针对ES + ik分词器优化）：
1. 必须补充产品型号（如没有则使用默认产品），放在句首
2. 保留所有关键技术词：产品型号、故障码、功能码、参数名等
3. 使用规范术语，如"变频器"、"报警"、"功能码"、"参数"等
4. 去掉无意义的口语词和助词，但保持句子可读性
5. 关键词之间可适当使用空格或标点分隔，便于分词匹配
6. 避免过长的修饰性短语，突出核心检索词

**示例**：
- 用户问题：显示E001报警怎么办？
- 改写为：MD630变频器 E001报警 如何解决

- 用户问题：f0-01功能码含义
- 改写为：MD630变频器 f0-01功能码 含义

**直接输出改写后的问题，不要输出其他内容。**"""

        try:
            response = await self.llm_client.do_llm(
                model_name=self.model_name,
                prompt="你是一个专业的变频器技术支持助手，擅长理解和改写用户问题。",
                content=prompt,
                max_tokens=500
            )
            response = self.llm_client.remove_think_tags(response)
            return response.strip()
        
        except Exception as e:
            # LLM调用失败，返回原问题
            return query
    
    async def _rewrite_multi_turn(
        self, 
        query: str, 
        context: str
    ) -> str:
        """
        多轮对话改写
        
        重点：结合上下文，改写为适合ES全文检索的表述（ik分词器优化）
        """
        prompt = f"""你是一个变频器技术支持助手。请结合上下文，将用户问题改写为适合Elasticsearch全文检索的表述。

**对话上下文**：
{context}

**当前问题**：{query}

**改写要求**（针对ES + ik分词器优化）：
1. 从上下文提取产品型号，放在句首
2. 补全代词（如"它"、"这个"）的具体指代（故障码、功能码等）
3. 保留所有关键技术词，使问题能独立理解
4. 使用规范术语，如"变频器"、"报警"、"功能码"、"参数"等
5. 关键词之间可适当使用空格或标点分隔，便于分词匹配
6. 去掉无意义的口语词和助词，但保持句子可读性

**示例**：
- 上下文：MD630变频器E001过热报警
- 用户问题：如何解决这个问题？
- 改写为：MD630变频器 E001过热报警 如何解决

- 上下文：MD630变频器E001报警
- 用户问题：参数怎么设置？
- 改写为：MD630变频器 E001报警 参数设置

**直接输出改写后的问题，不要输出其他内容。**"""

        try:
            response = await self.llm_client.do_llm(
                model_name=self.model_name,
                prompt="你是一个专业的变频器技术支持助手，擅长理解多轮对话。",
                content=prompt,
                max_tokens=500
            )
            response = self.llm_client.remove_think_tags(response)
            return response.strip()
        
        except Exception as e:
            # LLM调用失败，返回原问题
            return query


# 便捷函数
async def rewrite_query(
    input_message: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    便捷的问题改写函数
    
    Args:
        input_message: {
            "query": "用户问题",
            "context": {  # session.get() 返回的上下文
                "context": "上下文内容",
                "messages": [...]
            },
            "envs": {"product": "MD630"}  # 可选
        }
        config: 配置字典（可选，如果不提供会自动加载）
    
    Returns:
        {
            "rewritten_query": "改写后的问题"
        }
    """
    # 加载或使用配置
    if config is None:
        config = get_config()
    
    # 创建改写器
    rewriter = QueryRewriter(config)
    
    # 执行改写
    result = await rewriter.rewrite(input_message)
    
    return result


if __name__ == "__main__":
    import asyncio
    
    async def main():
        """测试改写功能"""
        print("=" * 60)
        print("问题改写测试")
        print("=" * 60)
        
        # 测试1：首轮对话（无上下文）
        print("\n📝 测试1: 首轮对话（使用默认产品）")
        input_msg = {
            "query": "详细解释下f0-01功能码含义",
            "context": {},  # 无上下文
            "envs": {
                "product": "MD630"
            }
        }
        
        result = await rewrite_query(input_msg)
        print(f"原问题: {input_msg['query']}")
        print(f"改写后: {result.get('rewritten_query')}")
        
        # 测试2：首轮对话（问题中包含产品）
        print("\n📝 测试2: 首轮对话（问题中包含产品）")
        input_msg = {
            "query": "MD605变频器显示E001报警，怎么处理？",
            "context": {},  # 无上下文
            "envs": {}
        }
        
        result = await rewrite_query(input_msg)
        print(f"原问题: {input_msg['query']}")
        print(f"改写后: {result.get('rewritten_query')}")
        
        # 测试3：多轮对话（有上下文）
        print("\n📝 测试3: 多轮对话（代词补全）")
        input_msg = {
            "query": "如何解决这个问题？",
            "context": {
                "context": "对话摘要: MD630变频器E001过热报警\n\n近期对话:\nUser: MD630显示E001\nAssistant: 这是过热保护",
                "messages": [
                    {"role": "user", "content": "MD630显示E001"},
                    {"role": "assistant", "content": "这是过热保护"}
                ]
            },
            "envs": {}
        }
        
        result = await rewrite_query(input_msg)
        print(f"原问题: {input_msg['query']}")
        print(f"改写后: {result.get('rewritten_query')}")
        
        print("\n" + "=" * 60)
        print("测试完成 - context由外部传入")
        print("=" * 60)
    
    # 运行测试
    asyncio.run(main())
