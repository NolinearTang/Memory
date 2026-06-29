import asyncio
from typing import List, Dict, Any, Optional
from core.models import SessionData, Message
from core.storage import SessionStorage
from retrieval.bm25_retriever import BM25Retriever
from core.summarizer import ConversationSummarizer


class SessionMemoryManager:
    
    def __init__(self, storage_dir: str = ".session_memory"):
        self.storage = SessionStorage(storage_dir)
        self.summarizer = ConversationSummarizer()
        
        self._processing_tasks: Dict[str, asyncio.Task] = {}
    
    async def add_message(
        self,
        session_id: str,
        messages: List[Message],
        fault_code: List[str] = None,
        function_code: List[str] = None,
        product_code: List[str] = None,
    ) -> Dict[str, Any]:
        # 处理默认值
        fault_code = fault_code or []
        function_code = function_code or []
        product_code = product_code or []
        
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        if self.storage.session_exists(session_id):
            session_data = self.storage.load_metadata(session_id)
        else:
            session_data = SessionData(
                session_id=session_id,
                fault_code=fault_code,
                function_code=function_code,
                product_code=product_code,
            )
        
        session_data.fault_code = list(set(session_data.fault_code + fault_code))
        session_data.function_code = list(set(session_data.function_code + function_code))
        session_data.product_code = list(set(session_data.product_code + product_code))
        
        self.storage.append_messages(session_id, message_dicts)
        
        all_messages = self.storage.read_all_messages(session_id)
        session_data.all_messages = all_messages
        
        self.storage.save_metadata(session_id, session_data)
        
        if session_id in self._processing_tasks:
            self._processing_tasks[session_id].cancel()
        
        task = asyncio.create_task(self._process_session_async(session_id))
        self._processing_tasks[session_id] = task
        
        return {
            "session_id": session_id,
            "message_count": len(message_dicts),
            "total_messages": len(all_messages),
        }
    
    async def _process_session_async(self, session_id: str):
        try:
            await asyncio.sleep(0.1)
            
            session_data = self.storage.load_metadata(session_id)
            if not session_data:
                return
            
            all_messages = session_data.all_messages
            KEEP_RECENT = 3  # 保留最近3轮（6条消息）作为recent_messages
            EARLY_START = 4  # 提前处理：第4轮（8条消息）就开始facts提取和摘要
            
            # ========== 1. 处理历史消息（增量摘要 + Facts提取） ==========
            # 优化点：提前处理，从第4轮开始，不用等到第6轮
            # 好处：更早地提取facts和生成摘要，后续get_message时能更快返回完整信息
            if len(all_messages) > EARLY_START * 2:
                old_end_idx = len(all_messages) - KEEP_RECENT * 2
                
                # 只处理新增的历史消息（增量处理）
                new_old_messages = all_messages[session_data.last_summarized_index:old_end_idx]
                
                if new_old_messages:
                    # 提取新的facts
                    new_facts = await self.summarizer.extract_facts(new_old_messages)
                    
                    # 整合facts：去重、更新冲突、合并
                    if new_facts or session_data.facts:
                        original_count = len(session_data.facts)
                        reconciled_facts = await self.summarizer.reconcile_facts(
                            existing_facts=session_data.facts,
                            new_messages=new_old_messages
                        )
                        session_data.facts = reconciled_facts
                        print(f"Facts整合: 原有{original_count}条 → 整合后{len(reconciled_facts)}条 (新提取{len(new_facts)}条)")
                    
                    # 增量更新摘要
                    if session_data.session_summary:
                        # 基于旧摘要更新
                        summary = await self.summarizer.update_summary(
                            old_summary=session_data.session_summary,
                            new_messages=new_old_messages,
                            facts=session_data.facts
                        )
                        print(f"增量更新摘要（新增 {len(new_old_messages)} 条消息）")
                    else:
                        # 首次生成摘要
                        summary = await self.summarizer.summarize_multiple_turns(new_old_messages)
                        print(f"首次生成摘要（{len(new_old_messages)} 条消息）")
                    
                    session_data.session_summary = summary
                    session_data.last_summarized_index = old_end_idx
                
                recent_messages = all_messages[-KEEP_RECENT * 2:]
            else:
                recent_messages = all_messages
            
            # ========== 2. 处理最近消息（利用缓存避免重复压缩） ==========
            processed_recent = []
            compressed_count = 0
            cached_count = 0
            
            for i, msg in enumerate(recent_messages):
                msg_idx = len(all_messages) - len(recent_messages) + i
                
                if msg["role"] == "assistant":
                    content = msg["content"]
                    
                    # 先检查缓存
                    if msg_idx in session_data.message_summaries:
                        # 使用缓存的压缩结果
                        compressed = session_data.message_summaries[msg_idx]
                        processed_recent.append({
                            "role": msg["role"],
                            "content": compressed,
                            "original_length": len(content),
                        })
                        cached_count += 1
                    elif len(content) > 200:
                        # 没有缓存且需要压缩
                        compressed = await self.summarizer.compress_long_answer(content, max_length=200)
                        processed_recent.append({
                            "role": msg["role"],
                            "content": compressed,
                            "original_length": len(content),
                        })
                        # 保存到缓存
                        session_data.message_summaries[msg_idx] = compressed
                        compressed_count += 1
                    else:
                        # 不需要压缩
                        processed_recent.append(msg)
                else:
                    processed_recent.append(msg)
            
            if compressed_count > 0 or cached_count > 0:
                print(f"消息压缩: 新压缩={compressed_count}, 使用缓存={cached_count}")
            
            session_data.recent_messages = processed_recent
            
            self.storage.save_metadata(session_id, session_data)
            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"处理session {session_id} 时出错: {e}")
        finally:
            if session_id in self._processing_tasks:
                del self._processing_tasks[session_id]
    
    async def get_message(
        self,
        session_id: str,
        query: str,
        top_k: int = 5,
        wait_for_processing: bool = False,  # 默认不等待，直接走兜底
        max_wait_seconds: float = 2.0,
    ) -> Dict[str, Any]:
        if not self.storage.session_exists(session_id):
            return {
                "code": 404,
                "message": "Session not found",
                "data": {},
            }
        
        # 兜底策略：如果有正在处理的任务，等待一小段时间
        is_processing = False
        if session_id in self._processing_tasks and wait_for_processing:
            task = self._processing_tasks[session_id]
            if not task.done():
                is_processing = True
                print(f"检测到session {session_id} 正在处理中，等待最多{max_wait_seconds}秒...")
                try:
                    await asyncio.wait_for(task, timeout=max_wait_seconds)
                    print(f"处理完成")
                except asyncio.TimeoutError:
                    print(f"等待超时，使用当前状态返回（可能不完整）")
                except Exception as e:
                    print(f"等待处理时出错: {e}")
        
        session_data = self.storage.load_metadata(session_id)
        
        state_info = self._format_state_info(session_data)
        
        # 检查是否仍在处理中
        still_processing = session_id in self._processing_tasks and not self._processing_tasks[session_id].done()
        
        context_info = await self._build_context(session_data, query, top_k, is_processing=still_processing)
        
        return {
            "code": 200,
            "message": "success" if not still_processing else "processing",
            "data": {
                "session_id": session_id,
                "state": state_info,
                "context": context_info,
                "is_processing": still_processing,  # 标记是否还在处理中
            },
        }
    
    def _format_state_info(self, session_data: SessionData) -> Dict[str, Any]:
        """格式化state信息为字典"""
        state_dict = {}
        
        if session_data.product_code:
            state_dict["product_code"] = session_data.product_code
        
        if session_data.fault_code:
            state_dict["fault_code"] = session_data.fault_code
        
        if session_data.function_code:
            state_dict["function_code"] = session_data.function_code
        
        return state_dict
    
    async def _build_context(
        self,
        session_data: SessionData,
        query: str,
        top_k: int,
        is_processing: bool = False,
    ) -> str:
        parts = []
        
        # 如果正在处理，添加提示（但仍然返回已有内容）
        if is_processing:
            parts.append("⚠️ 注意：当前会话正在后台处理中，以下facts和摘要可能不包含最新一轮对话的信息。")
        
        # 摘要信息（无论是否在处理，都返回已有的摘要）
        if session_data.session_summary:
            parts.append(f"对话摘要: {session_data.session_summary}")
        
        # Facts信息（无论是否在处理，都返回已有的facts）
        if session_data.facts:
            # 对facts进行相关性搜索
            relevant_facts = self._search_relevant_facts(session_data.facts, query, top_k=20)
            if relevant_facts:
                facts_text = "\n".join(f"- {fact}" for fact in relevant_facts)
                parts.append(f"关键事实:\n{facts_text}")
        else:
            # 兜底：如果facts为空，尝试从最近消息中快速提取基本信息
            if len(session_data.all_messages) >= 2:
                fallback_info = self._extract_fallback_info(session_data)
                if fallback_info:
                    parts.append(f"基本信息:\n{fallback_info}")
        
        # 近期对话：优先使用recent_messages，如果为空则从all_messages取最新的
        # 确保不等待状态下也能拿到最新对话
        if session_data.recent_messages:
            recent_text = self._format_messages(session_data.recent_messages)
            parts.append(f"近期对话:\n{recent_text}")
        elif session_data.all_messages:
            # 兜底：如果recent_messages为空，从all_messages取最新6条（3轮）
            recent_msgs = session_data.all_messages[-6:]
            recent_text = self._format_messages(recent_msgs)
            parts.append(f"近期对话:\n{recent_text}")
        
        if query and session_data.all_messages:
            retriever = BM25Retriever()
            
            docs = [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "index": idx,
                }
                for idx, msg in enumerate(session_data.all_messages)
            ]
            
            retriever.add_documents(docs)
            
            results = retriever.search(query, top_k=top_k)
            
            if results:
                relevant_text = ""
                for doc, score in results:
                    relevant_text += f"- [{doc['role']}]: {doc['content']}\n"
                parts.append(f"相关对话:\n{relevant_text}")
        
        return "\n\n".join(parts)
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        formatted = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            formatted.append(f"[{role}]: {content}")
        return "\n".join(formatted)
    
    def _search_relevant_facts(self, facts: List[str], query: str, top_k: int = 20) -> List[str]:
        """
        对facts进行相关性搜索，返回与query最相关的facts
        如果query为空，返回全部facts（最多top_k条）
        """
        if not facts:
            return []
        
        # 如果query为空，返回全部facts（最多top_k条）
        if not query or not query.strip():
            return facts[:top_k]
        
        # 使用BM25搜索相关facts
        retriever = BM25Retriever()
        
        # 将facts转换为文档格式
        docs = [
            {"content": fact, "index": idx}
            for idx, fact in enumerate(facts)
        ]
        
        retriever.add_documents(docs)
        results = retriever.search(query, top_k=min(top_k, len(facts)))
        
        # 提取搜索到的facts（按相关性排序）
        relevant_facts = [doc["content"] for doc, score in results]
        
        return relevant_facts
    
    def _extract_fallback_info(self, session_data: SessionData) -> str:
        """
        兜底策略：当facts为空时，从消息中快速提取基本信息
        使用简单的规则匹配，不调用LLM
        """
        fallback_items = []
        
        # 从state提取基本信息
        if session_data.product_code:
            fallback_items.append(f"涉及产品: {', '.join(session_data.product_code)}")
        if session_data.fault_code:
            fallback_items.append(f"故障码: {', '.join(session_data.fault_code)}")
        if session_data.function_code:
            fallback_items.append(f"功能码: {', '.join(session_data.function_code)}")
        
        # 从最近3条消息中提取关键词（简单规则）
        recent_msgs = session_data.all_messages[-3:] if len(session_data.all_messages) >= 3 else session_data.all_messages
        all_text = " ".join([msg.get("content", "") for msg in recent_msgs])
        
        # 简单的关键词匹配
        import re
        
        # 提取型号（如：MD630, S7-1200等）
        models = re.findall(r'\b[A-Z]{2,}\d{2,}\b', all_text)
        if models:
            fallback_items.append(f"提及型号: {', '.join(set(models[:3]))}")
        
        # 提取参数（如：P01, F0-01等）
        params = re.findall(r'\b[PFpf]\d{1,2}(?:-\d{2})?\b', all_text)
        if params:
            fallback_items.append(f"提及参数: {', '.join(set(params[:3]))}")
        
        return "\n".join(fallback_items) if fallback_items else ""
    
    def list_sessions(self) -> List[str]:
        return self.storage.list_sessions()
    
    async def shutdown(self):
        for task in self._processing_tasks.values():
            task.cancel()
        
        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks.values(), return_exceptions=True)
        
        self._processing_tasks.clear()
