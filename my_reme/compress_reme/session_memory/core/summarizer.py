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
    
    async def extract_facts(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        从对话中提取客观事实
        重点提取：
        1. 设备型号、产品信息
        2. 故障码和故障现象
        3. 参数设置和配置信息
        4. 用户澄清或纠正的内容（优先级最高）
        5. 已确认的解决方案
        """
        if not messages:
            return []
        
        conversation_text = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"
        
        # 从配置文件读取prompts
        system_prompt = self.prompts_config["system_prompts"].get(
            "fact_extraction",
            "你是工控领域的信息提取专家，擅长从技术对话中提取关键事实，特别关注用户澄清的内容。"
        )
        user_prompt_template = self.prompts_config["user_prompts"].get(
            "fact_extraction", 
            {"template": "请从以下对话中提取关键事实：\n{conversation_text}\n\n请列出事实："}
        )["template"]
        llm_params = self.prompts_config["llm_parameters"].get(
            "fact_extraction",
            {"temperature": 0.1, "max_tokens": 800}
        )
        
        user_prompt = user_prompt_template.format(conversation_text=conversation_text)
        
        try:
            result = await self.client.do_llm(
                model_name=self.selected_model,
                prompt=system_prompt,
                content=user_prompt,
                max_tokens=llm_params["max_tokens"]
            )
            
            # 解析返回的事实列表（假设每行一个事实）
            facts = [f.strip() for f in result.split('\n') if f.strip() and not f.strip().startswith('#')]
            # 去除可能的序号标记
            facts = [f.lstrip('- ').lstrip('• ').lstrip('*').strip() for f in facts]
            facts = [f for f in facts if f]  # 去除空字符串
            
            return facts
        
        except Exception as e:
            print(f"Facts提取失败: {e}")
            return []
    
    async def update_summary(
        self, 
        old_summary: str, 
        new_messages: List[Dict[str, str]],
        facts: List[str] = None
    ) -> str:
        """
        增量更新摘要：基于旧摘要和新消息生成新摘要
        """
        if not new_messages:
            return old_summary
        
        conversation_text = ""
        for msg in new_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"
        
        facts_text = "\n".join(f"- {fact}" for fact in facts) if facts else "无"
        
        # 从配置文件读取prompts
        system_prompt = self.prompts_config["system_prompts"].get(
            "incremental_summary",
            "你是工控领域的技术摘要专家，擅长更新和整合技术对话摘要。"
        )
        user_prompt_template = self.prompts_config["user_prompts"].get(
            "incremental_summary",
            {"template": "旧摘要：\n{old_summary}\n\n新对话：\n{new_conversation}\n\n关键事实：\n{facts}\n\n请生成更新后的摘要："}
        )["template"]
        llm_params = self.prompts_config["llm_parameters"].get(
            "incremental_summary",
            {"temperature": 0.1, "max_tokens": 1500}
        )
        
        user_prompt = user_prompt_template.format(
            old_summary=old_summary,
            new_conversation=conversation_text,
            facts=facts_text
        )
        
        try:
            summary = await self.client.do_llm(
                model_name=self.selected_model,
                prompt=system_prompt,
                content=user_prompt,
                max_tokens=llm_params["max_tokens"]
            )
            
            return summary or old_summary
        
        except Exception as e:
            print(f"增量摘要生成失败: {e}")
            return old_summary
    
    async def reconcile_facts(
        self,
        existing_facts: List[str],
        new_messages: List[Dict[str, str]]
    ) -> List[str]:
        """
        整合和更新facts列表
        功能：
        1. 去重
        2. 识别冲突并更新（用户澄清优先）
        3. 合并新旧facts
        """
        if not new_messages:
            # 没有新消息，只做去重
            return list(dict.fromkeys(existing_facts))
        
        # 构建新对话文本
        conversation_text = ""
        for msg in new_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"
        
        # 构建现有facts文本
        existing_facts_text = "\n".join(f"- {fact}" for fact in existing_facts) if existing_facts else "无"
        
        # 从配置文件读取prompts
        system_prompt = self.prompts_config["system_prompts"].get(
            "fact_reconciliation",
            "你是工控领域的信息整合专家，擅长整理、去重和更新技术对话中的事实信息。"
        )
        user_prompt_template = self.prompts_config["user_prompts"].get(
            "fact_reconciliation",
            {"template": "现有事实：\n{existing_facts}\n\n新对话：\n{new_conversation}\n\n请整合facts："}
        )["template"]
        llm_params = self.prompts_config["llm_parameters"].get(
            "fact_reconciliation",
            {"temperature": 0.1, "max_tokens": 1000}
        )
        
        user_prompt = user_prompt_template.format(
            existing_facts=existing_facts_text,
            new_conversation=conversation_text
        )
        
        try:
            result = await self.client.do_llm(
                model_name=self.selected_model,
                prompt=system_prompt,
                content=user_prompt,
                max_tokens=llm_params["max_tokens"]
            )
            
            # 解析返回的facts列表
            reconciled_facts = [f.strip() for f in result.split('\n') if f.strip() and not f.strip().startswith('#')]
            # 去除可能的序号标记
            reconciled_facts = [f.lstrip('- ').lstrip('• ').lstrip('*').lstrip('1234567890.').strip() for f in reconciled_facts]
            reconciled_facts = [f for f in reconciled_facts if f]  # 去除空字符串
            
            # 如果LLM返回的结果为空或异常，至少保留去重后的现有facts
            if not reconciled_facts:
                reconciled_facts = list(dict.fromkeys(existing_facts))
            
            # 限制最多100个facts，优先保留最新的
            if len(reconciled_facts) > 100:
                print(f"Facts数量超过100（当前{len(reconciled_facts)}），保留最新的100条")
                reconciled_facts = reconciled_facts[-100:]
            
            return reconciled_facts
        
        except Exception as e:
            print(f"Facts整合失败: {e}")
            # 失败时返回去重后的现有facts
            return list(dict.fromkeys(existing_facts))
