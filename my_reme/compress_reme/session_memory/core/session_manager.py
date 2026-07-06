import asyncio
from typing import List, Dict, Any, Optional
from core.models import SessionData, Message
from core.storage import SessionStorage
from retrieval.bm25_retriever import BM25Retriever
from core.summarizer import ConversationSummarizer


class SessionMemoryManager:
    
    def __init__(self, storage_dir: str = ".session_memory", storage=None):
        self.storage = storage if storage is not None else SessionStorage(storage_dir)
        self.summarizer = ConversationSummarizer()
        
        self._processing_tasks: Dict[str, asyncio.Task] = {}
    
    async def add_message(
        self,
        session_id: str,
        messages: List[Message],
        fault_code: List[str] = None,
        function_code: List[str] = None,
        product_code: List[str] = None,
        user_id: Optional[str] = None,
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
        
        # 注册用户-会话映射（user_id 不传时用 session_id 代替）
        effective_user_id = user_id or session_id
        self.storage.register_user_session(effective_user_id, session_id)
        
        # 第一轮（<=2条消息）不触发异步处理
        # 因为单轮问答场景很常见，触发处理没有意义
        if len(all_messages) > 2:
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
            KEEP_RECENT = 3      # 近期对话显示最近3轮（6条消息）
            EXTRACT_BUFFER = 2   # summary提取缓冲：保留最近2轮不提取
            
            # ========== Phase 1a: Facts 实时更新（无缓冲，每轮都处理） ==========
            # 每次处理所有新增消息，确保最新一轮的facts也被及时整合
            facts_end_idx = len(all_messages)
            new_facts_messages = all_messages[session_data.last_facts_index:facts_end_idx]
            
            if new_facts_messages:
                original_count = len(session_data.facts)
                reconciled_facts = await self.summarizer.reconcile_facts(
                    existing_facts=session_data.facts,
                    new_messages=new_facts_messages
                )
                session_data.facts = reconciled_facts
                session_data.last_facts_index = facts_end_idx
                print(f"Phase 1a: Facts实时更新（新增{len(new_facts_messages)}条消息，{original_count}条 → {len(reconciled_facts)}条）")
                
                # ✅ Facts 更新后立即保存
                self.storage.save_metadata(session_id, session_data)
            
            # ========== Phase 1b: Summary 更新（保留最近2轮缓冲） ==========
            # summary开销大，保留缓冲，第3轮开始处理
            if len(all_messages) > EXTRACT_BUFFER * 2:
                summary_end_idx = len(all_messages) - EXTRACT_BUFFER * 2
                new_summary_messages = all_messages[session_data.last_summarized_index:summary_end_idx]
                
                if new_summary_messages:
                    if session_data.session_summary:
                        summary = await self.summarizer.update_summary(
                            old_summary=session_data.session_summary,
                            new_messages=new_summary_messages,
                            facts=session_data.facts
                        )
                        print(f"Phase 1b: 增量更新摘要（新增 {len(new_summary_messages)} 条消息）")
                    else:
                        summary = await self.summarizer.summarize_multiple_turns(new_summary_messages)
                        print(f"Phase 1b: 首次生成摘要（{len(new_summary_messages)} 条消息）")
                    
                    session_data.session_summary = summary
                    session_data.last_summarized_index = summary_end_idx
                    
                    # ✅ Summary 更新后立即保存
                    self.storage.save_metadata(session_id, session_data)
                    print(f"Phase 1b 完成：summary已保存（覆盖到第{summary_end_idx // 2}轮）")
            
            # ========== Phase 2: 压缩近3轮消息（利用缓存） ==========
            if len(all_messages) > KEEP_RECENT * 2:
                recent_messages = all_messages[-KEEP_RECENT * 2:]
            else:
                recent_messages = all_messages
            
            processed_recent = []
            compressed_count = 0
            cached_count = 0
            
            for i, msg in enumerate(recent_messages):
                msg_idx = len(all_messages) - len(recent_messages) + i
                
                if msg["role"] == "assistant":
                    content = msg["content"]
                    
                    # 先检查缓存
                    if msg_idx in session_data.message_summaries:
                        compressed = session_data.message_summaries[msg_idx]
                        processed_recent.append({
                            "role": msg["role"],
                            "content": compressed,
                            "original_length": len(content),
                        })
                        cached_count += 1
                    elif len(content) > 200:
                        compressed = await self.summarizer.compress_long_answer(content, max_length=200)
                        processed_recent.append({
                            "role": msg["role"],
                            "content": compressed,
                            "original_length": len(content),
                        })
                        session_data.message_summaries[msg_idx] = compressed
                        compressed_count += 1
                    else:
                        processed_recent.append(msg)
                else:
                    processed_recent.append(msg)
            
            if compressed_count > 0 or cached_count > 0:
                print(f"Phase 2 消息压缩: 新压缩={compressed_count}, 使用缓存={cached_count}")
            
            session_data.recent_messages = processed_recent
            
            # Phase 2 完成后再保存一次
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
    ) -> Dict[str, Any]:
        if not self.storage.session_exists(session_id):
            return {
                "code": 404,
                "message": "Session not found",
                "data": {},
            }
        
        # 完全不等待，直接读取已落盘的数据
        # facts/summary已包含[:-3]轮的信息（上次处理已保存）
        # 近期对话利用message_summaries缓存智能组装
        session_data = self.storage.load_metadata(session_id)
        
        state_info = self._format_state_info(session_data)
        
        # 对facts进行相关性搜索（如果有query）- 只搜索一次
        relevant_facts = []
        if session_data.facts:
            relevant_facts = self._search_relevant_facts(session_data.facts, query, top_k=20)
        
        context_info = await self._build_context(
            session_data, query, top_k,
            relevant_facts=relevant_facts
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "session_id": session_id,
                "state": state_info,
                "facts": relevant_facts,
                "context": context_info,
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
        relevant_facts: List[str] = None,  # 接收已搜索好的facts
    ) -> str:
        parts = []
        
        # 摘要信息（上次处理已保存，覆盖[:-3]轮）
        if session_data.session_summary:
            parts.append(f"对话摘要: {session_data.session_summary}")
        
        # Facts信息（上次处理已保存，覆盖[:-3]轮）
        if relevant_facts:
            facts_text = "\n".join(f"- {fact}" for fact in relevant_facts)
            parts.append(f"关键事实:\n{facts_text}")
        elif session_data.facts:
            facts_text = "\n".join(f"- {fact}" for fact in session_data.facts[:20])
            parts.append(f"关键事实:\n{facts_text}")
        else:
            # 兜底：如果facts为空，尝试从最近消息中快速提取基本信息
            if len(session_data.all_messages) >= 2:
                fallback_info = self._extract_fallback_info(session_data)
                if fallback_info:
                    parts.append(f"基本信息:\n{fallback_info}")
        
        # 近期对话：优先使用recent_messages，否则利用message_summaries缓存智能组装
        if session_data.recent_messages:
            recent_text = self._format_messages(session_data.recent_messages)
            parts.append(f"近期对话:\n{recent_text}")
        elif session_data.all_messages:
            # 智能兜底：利用message_summaries缓存
            # 第2-3轮（上次处理时已压缩）用缓存，最新1轮用原始消息
            KEEP_RECENT = 3
            recent_raw = session_data.all_messages[-(KEEP_RECENT * 2):]
            start_idx = len(session_data.all_messages) - len(recent_raw)
            
            smart_recent = []
            for i, msg in enumerate(recent_raw):
                msg_idx = start_idx + i
                if msg["role"] == "assistant" and msg_idx in session_data.message_summaries:
                    # 使用缓存的压缩版本（上次处理已压缩）
                    smart_recent.append({
                        "role": msg["role"],
                        "content": session_data.message_summaries[msg_idx],
                    })
                else:
                    # 用原始消息（最新1轮或user消息）
                    smart_recent.append(msg)
            
            recent_text = self._format_messages(smart_recent)
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

    def list_sessions_by_user(self, user_id: str) -> List[str]:
        return self.storage.list_sessions_by_user(user_id)
    
    async def shutdown(self):
        for task in self._processing_tasks.values():
            task.cancel()
        
        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks.values(), return_exceptions=True)
        
        self._processing_tasks.clear()
