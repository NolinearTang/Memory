import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from core.llm_client import LlmClient
from config import get_config


class ConversationSummarizer:
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "gpt-4", prompts_file: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4")
        
        # 使用LlmClient - 需要传递完整配置（包含model_hub）
        kllm_config = get_config()
        self.client = LlmClient(kllm_config)
        
        # 获取选中的模型名称
        self.selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
        
        # 加载prompts配置
        if prompts_file is None:
            prompts_file = Path(__file__).parent.parent / "prompts" / "prompts.json"
        else:
            prompts_file = Path(prompts_file)
        
        self.prompts_config = self._load_prompts(prompts_file)
    
    def _load_prompts(self, prompts_file: Path) -> Dict:
        """加载prompts配置文件"""
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: prompts配置文件 {prompts_file} 不存在，使用默认配置")
            return self._get_default_prompts()
        except json.JSONDecodeError as e:
            print(f"警告: prompts配置文件解析失败: {e}，使用默认配置")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict:
        """默认prompts配置（备用）"""
        return {
            "system_prompts": {
                "basic_summary": "你是工控领域的技术专家。",
                "long_answer_compression": "你是工控领域的技术文档压缩专家。",
                "multi_turn_summary": "你是工控领域的资深技术专家。"
            },
            "user_prompts": {
                "basic_summary": {"template": "请摘要：\n{conversation_text}", "max_chars": 150},
                "long_answer_compression": {"template": "请压缩：\n{answer}", "max_chars": 200},
                "multi_turn_summary": {"template": "请摘要：\n{conversation_text}", "max_chars": 1000}
            },
            "llm_parameters": {
                "basic_summary": {"temperature": 0.1, "max_tokens": 500},
                "long_answer_compression": {"temperature": 0.1, "max_tokens": 300},
                "multi_turn_summary": {"temperature": 0.1, "max_tokens": 1500}
            }
        }
    
    
    async def compress_long_answer(self, answer: str, max_length: int = 200) -> str:
        if len(answer) <= max_length:
            return answer
        
        # 从配置文件读取prompts
        system_prompt = self.prompts_config["system_prompts"]["long_answer_compression"]
        user_prompt_template = self.prompts_config["user_prompts"]["long_answer_compression"]["template"]
        llm_params = self.prompts_config["llm_parameters"]["long_answer_compression"]
        
        # 填充模板
        user_prompt = user_prompt_template.format(answer=answer, max_length=max_length)
        
        try:
            # 直接调用do_llm（它本身就是async）
            compressed = await self.client.do_llm(
                model_name=self.selected_model,
                prompt=system_prompt,
                content=user_prompt,
                max_tokens=llm_params["max_tokens"]
            )
            
            return compressed or answer[:max_length]
        
        except Exception as e:
            print(f"压缩失败: {e}")
            return answer[:max_length]
    
    async def summarize_multiple_turns(self, messages: List[Dict[str, str]], max_turns: int = 6) -> str:
        if not messages:
            return ""
        
        conversation_text = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"
        
        # 根据消息数量选择不同的提示词配置
        if len(messages) <= max_turns:
            # 少量消息使用基础摘要
            prompt_key = "basic_summary"
        else:
            # 多轮对话使用详细摘要
            prompt_key = "multi_turn_summary"
        
        # 从配置文件读取prompts
        system_prompt = self.prompts_config["system_prompts"][prompt_key]
        user_prompt_template = self.prompts_config["user_prompts"][prompt_key]["template"]
        llm_params = self.prompts_config["llm_parameters"][prompt_key]
        
        # 填充模板
        user_prompt = user_prompt_template.format(
            conversation_text=conversation_text,
            message_count=len(messages)
        )
        
        try:
            # 直接调用do_llm（它本身就是async）
            summary = await self.client.do_llm(
                model_name=self.selected_model,
                prompt=system_prompt,
                content=user_prompt,
                max_tokens=llm_params["max_tokens"]
            )
            
            return summary or ""
        
        except Exception as e:
            print(f"摘要生成失败: {e}")
            return ""
