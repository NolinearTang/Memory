#!/usr/bin/env python3
"""
基于大模型的拒答判断模块

使用大模型智能分析上下文，判断是否需要拒答用户问题
"""

from typing import Optional, Dict, Any
import asyncio

from core.llm_client import LlmClient


class LLMRejectionChecker:
    """基于大模型的拒答判断器"""
    
    def __init__(self, kllm_config: Dict[str, Any]):
        """
        初始化拒答判断器
        
        Args:
            kllm_config: LLM配置字典（从 config.config 获取），包含：
                - model_hub: 模型配置字典，每个模型包含 api_key, base_url, model_name 等
                - llm.selected_model: 选择使用的模型名称
        """
        self.llm_client = LlmClient(kllm_config)
        self.model_name = kllm_config.get("llm", {}).get("selected_model")
        
        # 支持的变频器型号列表
        self.supported_models_text = """
支持的变频器型号：
- MD600 系列：包括 MD600 及其所有变种型号
- MD605 系列：包括 MD605 及其所有变种型号
- MD630 系列：包括 MD630、MD630S、MD630S-4T0750G/P 等所有变种型号
"""
        
        # 不支持的变频器型号列表
        self.unsupported_models_text = """
不支持的变频器型号：
- MD580 系列
- MD880 系列
- 其他 MD xxx 系列（除了 MD600/605/630）
- HD30 系列
- HD33 系列
- BPJ 系列
- BPJV 系列
- 其他根据上下文能确定是变频器，但不在支持的变频器型号的产品
"""
    
    def build_system_prompt(self) -> str:
        """
        构建系统提示词
        
        Returns:
            系统提示词
        """
        return f"""你是一个工控变频器问答系统的拒答判断助手。你的任务是分析用户的问题，判断是否需要拒答。

{self.supported_models_text}

{self.unsupported_models_text}

【判断规则】
1. 如果用户询问的是支持的变频器型号（MD600/605/630系列），输出：不拒答
2. 如果用户询问的是明确不支持的变频器型号，输出：拒答
3. 如果用户询问的不是变频器产品（如伺服电机、PLC等其他产品），输出：拒答
4. 如果用户询问的是变频器，但没有提及具体型号，或者型号不明确，输出：不拒答（谨慎拒答原则）
5. 如果从上下文可以推断出用户询问的是不支持的型号，也要拒答

【输出格式】
只能输出以下两种格式之一：
1. 不拒答
2. 暂不支持xxx产品

注意：
- 如果判断为不拒答，只输出"不拒答"三个字
- 如果判断为拒答，输出"暂不支持xxx产品"，其中xxx替换为具体的产品型号或产品类型
- 例如：暂不支持MD580产品、暂不支持伺服电机产品、暂不支持HD30产品
- 不要输出任何其他内容，不要解释，不要多余的文字"""
    
    def build_user_input(
        self,
        context: str,
        original_question: str,
        rewritten_question: str
    ) -> str:
        """
        构建用户输入
        
        Args:
            context: 上下文信息
            original_question: 原始问题
            rewritten_question: 改写后的问题
            
        Returns:
            用户输入内容
        """
        return f"""【上下文】
{context if context else "无"}

【原始问题】
{original_question}

【改写后的问题】
{rewritten_question if rewritten_question else "无"}"""
    
    async def call_llm(self, system_prompt, user_input, **kwargs):
        """
        调用大模型API
        
        Args:
            system_prompt: 系统提示词
            user_input: 用户输入
            
        Returns:
            大模型返回的字符串结果
        """

        model_name = kwargs.pop("model_name", self.model_name)
        try:
            # 使用 LlmClient 调用大模型
            content = await self.llm_client.do_llm(
                model_name=model_name,
                prompt=system_prompt,
                content=user_input,
                **kwargs
            )
            
            return content.strip() if content else None
            
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return None
    
    async def check_rejection(
        self,
        context: str = "",
        original_question: str = "",
        rewritten_question: str = ""
    ) -> Optional[str]:
        """
        检查是否需要拒答
        
        Args:
            context: 上下文信息（可选）
            original_question: 原始问题
            rewritten_question: 改写后的问题
            
        Returns:
            - None: 不拒答，可以正常回答
            - str: 拒答话术，格式为"暂不支持xxx产品。"
        """
        # 构建系统提示词和用户输入
        system_prompt = self.build_system_prompt()
        user_input = self.build_user_input(context, original_question, rewritten_question)
        
        # 调用大模型
        result = await self.call_llm(system_prompt, user_input)
        
        if not result:
            # 如果大模型调用失败，采用谨慎原则：允许作答
            return None
        
        # 判断返回结果
        if result == "不拒答":
            return None
        elif result.startswith("暂不支持") and result.endswith("产品"):
            return result
        else:
            # 其他情况，采用谨慎原则：允许作答
            return None
    


async def main():
    """测试示例"""
    
    # 从 config.py 导入配置
    from config.config import get_config
    kllm_config = get_config()
    
    checker = LLMRejectionChecker(kllm_config=kllm_config)
    
    # 测试用例
    test_cases = [
        {
            "context": "",
            "original_question": "MD630变频器如何配置参数？",
            "rewritten_question": "MD630变频器的参数配置方法是什么？",
            "expected": False,
            "note": "MD630支持"
        },
        {
            "context": "",
            "original_question": "MD630S-4T0750G/P变频器怎么使用？",
            "rewritten_question": "MD630S-4T0750G/P变频器的使用方法",
            "expected": False,
            "note": "MD630系列支持"
        },
        {
            "context": "",
            "original_question": "MD580变频器故障代码E01是什么意思？",
            "rewritten_question": "MD580变频器E01故障代码含义",
            "expected": True,
            "note": "MD580不支持"
        },
        {
            "context": "",
            "original_question": "MD880系列变频器支持哪些通讯协议？",
            "rewritten_question": "MD880变频器的通讯协议",
            "expected": True,
            "note": "MD880不支持"
        },
        {
            "context": "",
            "original_question": "伺服电机如何选型？",
            "rewritten_question": "伺服电机选型方法",
            "expected": True,
            "note": "非变频器产品，应拒答"
        },
        {
            "context": "",
            "original_question": "变频器怎么设置频率？",
            "rewritten_question": "变频器频率设置方法",
            "expected": False,
            "note": "无型号，谨慎不拒答"
        },
        {
            "context": "用户之前询问过MD630变频器相关问题",
            "original_question": "那MD580呢？",
            "rewritten_question": "MD580变频器的情况如何？",
            "expected": True,
            "note": "根据上下文判断MD580不支持"
        },
    ]
    
    print("=" * 80)
    print("基于大模型的拒答判断测试")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test['note']}")
        print(f"  原始问题: {test['original_question']}")
        print(f"  改写问题: {test['rewritten_question']}")
        
        rejection_message = await checker.check_rejection(
            context=test['context'],
            original_question=test['original_question'],
            rewritten_question=test['rewritten_question']
        )
        
        should_reject = rejection_message is not None
        result = "拒答" if should_reject else "可以作答"
        expected = "拒答" if test['expected'] else "可以作答"
        status = "✓" if should_reject == test['expected'] else "✗"
        
        print(f"  判断结果: {result}")
        if rejection_message:
            print(f"  拒答话术: {rejection_message}")
        print(f"  预期结果: {expected}")
        print(f"  测试状态: {status}")
        
        if should_reject == test['expected']:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"测试完成: 通过 {passed}/{len(test_cases)}，失败 {failed}/{len(test_cases)}")
    print("=" * 80)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
