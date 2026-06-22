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
            
            KEEP_RECENT = 3
            
            if len(all_messages) > KEEP_RECENT * 2:
                old_messages = all_messages[:-KEEP_RECENT * 2]
                
                if old_messages:
                    summary = await self.summarizer.summarize_multiple_turns(old_messages)
                    session_data.session_summary = summary
                
                recent_messages = all_messages[-KEEP_RECENT * 2:]
            else:
                recent_messages = all_messages
            
            processed_recent = []
            for i, msg in enumerate(recent_messages):
                if msg["role"] == "assistant":
                    content = msg["content"]
                    if len(content) > 200:
                        compressed = await self.summarizer.compress_long_answer(content, max_length=200)
                        processed_recent.append({
                            "role": msg["role"],
                            "content": compressed,
                            "original_length": len(content),
                        })
                        
                        msg_idx = len(all_messages) - len(recent_messages) + i
                        session_data.message_summaries[msg_idx] = compressed
                    else:
                        processed_recent.append(msg)
                else:
                    processed_recent.append(msg)
            
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
    ) -> Dict[str, Any]:
        if not self.storage.session_exists(session_id):
            return {
                "code": 404,
                "message": "Session not found",
                "data": {},
            }
        
        session_data = self.storage.load_metadata(session_id)
        
        state_info = self._format_state_info(session_data)
        
        context_info = await self._build_context(session_data, query, top_k)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "session_id": session_id,
                "state": state_info,
                "context": context_info,
            },
        }
    
    def _format_state_info(self, session_data: SessionData) -> str:
        parts = []
        
        if session_data.product_code:
            parts.append(f"产品信息: {session_data.product_code}")
        
        if session_data.fault_code:
            parts.append(f"故障码: {session_data.fault_code}")
        
        if session_data.function_code:
            parts.append(f"功能码: {session_data.function_code}")
        
        return ", ".join(parts)
    
    async def _build_context(
        self,
        session_data: SessionData,
        query: str,
        top_k: int,
    ) -> str:
        parts = []
        
        if session_data.session_summary:
            parts.append(f"对话摘要: {session_data.session_summary}")
        
        if session_data.recent_messages:
            recent_text = self._format_messages(session_data.recent_messages)
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
    
    def list_sessions(self) -> List[str]:
        return self.storage.list_sessions()
    
    async def shutdown(self):
        for task in self._processing_tasks.values():
            task.cancel()
        
        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks.values(), return_exceptions=True)
        
        self._processing_tasks.clear()
