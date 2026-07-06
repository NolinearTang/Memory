import argparse
import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.session_manager import SessionMemoryManager
from core.models import AddMessageRequest, AddMessageResponse, GetMessageRequest, GetMessageResponse
from core.llm_client import LlmClient
from config import kllm_config
from pydantic import BaseModel
import os
from redis_handler.redis_client import RedisClient
from redis_handler.session_storage_redis import RedisSessionStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _init_redis_storage() -> RedisSessionStorage:
    """从 kllm_config 初始化 Redis 存储"""
    redis_cfg = kllm_config.get('redis', {})
    conn_cfg = {
        'host': redis_cfg.get('host', 'localhost'),
        'port': redis_cfg.get('port', 6379),
        'db': redis_cfg.get('db', 0),
        'decode_responses': redis_cfg.get('decode_responses', True),
    }
    if redis_cfg.get('password'):
        conn_cfg['password'] = redis_cfg['password']
    client = RedisClient(conn_cfg)
    client.connect()
    ttl_cfg = redis_cfg.get('ttl', {})
    storage = RedisSessionStorage(
        redis_client=client,
        single_turn_ttl=ttl_cfg.get('single_turn', 604800),
        multi_turn_ttl=ttl_cfg.get('multi_turn', 2592000),
    )
    logger.info(f"✅ Redis 存储已连接: {conn_cfg['host']}:{conn_cfg['port']}")
    return storage

app = FastAPI(
    title="Session Memory服务",
    description="基于对话摘要和BM25检索的会话记忆服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager: SessionMemoryManager | None = None
llm_client: LlmClient | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str = None  # 可选，会话 ID
    context: str = None     # 可选，从 get_session 返回的上下文


class ChatResponse(BaseModel):
    reply: str
    usage: dict = None


@app.on_event("startup")
async def startup_event():
    global manager, llm_client
    
    # 初始化 LLM 客户端
    try:
        selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
        model_config = kllm_config.get('model_hub', {}).get(selected_model)
        if not model_config:
            raise ValueError(f"模型 '{selected_model}' 在 model_hub 中未找到")
        logger.info(f"📋 使用模型: {selected_model} ({model_config.get('model_name')})")
        llm_client = LlmClient(kllm_config)
        logger.info("✅ LLM客户端初始化成功")
    except Exception as e:
        logger.error(f"❌ LLM客户端初始化失败: {e}")
        llm_client = None
    
    # 初始化 Redis 存储
    storage = _init_redis_storage()
    manager = SessionMemoryManager(storage=storage)
    logger.info("Session Memory服务器启动成功")


@app.on_event("shutdown")
async def shutdown_event():
    global manager
    if manager:
        await manager.shutdown()
    logger.info("Session Memory服务器已关闭")


@app.get("/")
async def root():
    """API服务信息 - 纯后端服务，不耦合前端"""
    return {
        "service": "Session Memory API",
        "version": "1.1.0",
        "description": "基于对话摘要和BM25检索的会话记忆服务",
        "endpoints": {
            "POST /chat": "简单LLM对话",
            "POST /add_message": "添加对话消息到会话",
            "POST /get_message": "获取会话上下文",
            "GET /sessions": "列出所有会话",
            "GET /health": "健康检查",
            "GET /docs": "API文档（Swagger）",
        },
        "test_ui": {
            "GET /chat-ui": "聊天界面（LLM对话）",
        },
        "model": kllm_config.get('llm', {}).get('selected_model', 'unknown'),
    }



@app.get("/config")
async def get_current_config():
    """获取当前配置信息（供前端使用）"""
    selected_model = kllm_config.get('llm', {}).get('selected_model', 'unknown')
    model_config = kllm_config.get('model_hub', {}).get(selected_model, {})
    return {
        "selected_model": selected_model,
        "model_name": model_config.get('model_name', 'unknown'),
        "temperature": model_config.get('temperature', 0.7),
        "max_tokens": model_config.get('max_tokens', 1000),
        "available_models": list(kllm_config.get('model_hub', {}).keys()),
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions": len(manager.list_sessions()) if manager else 0,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口 - 支持session上下文和自动保存
    """
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM客户端未初始化，请检查配置")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    try:
        session_id = request.session_id or "default_session"
        logger.info(f"[{session_id}] 收到聊天请求: {request.message[:50]}...")
        
        # 获取当前模型配置
        selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
        model_config = kllm_config.get('model_hub', {}).get(selected_model, {})
        
        # 1. 如果有session_id，获取上下文
        context_str = ""
        if request.session_id and manager:
            try:
                result = await manager.get_message(session_id=session_id, query=request.message, top_k=3)
                
                # get_message 返回: {"code": 200, "data": {"context": "...", "state": "..."}}
                if result.get('code') == 200:
                    data = result.get('data', {})
                    context_str = data.get('context', '')
                    
                    if context_str:
                        logger.info(f"[{session_id}] 获取到上下文，长度: {len(context_str)}")
                        logger.debug(f"[{session_id}] 上下文内容: {context_str[:200]}...")
                    else:
                        logger.info(f"[{session_id}] 当前没有历史上下文")
                else:
                    logger.warning(f"[{session_id}] 获取上下文失败: {result.get('message')}")
            except Exception as e:
                logger.warning(f"[{session_id}] 获取上下文失败: {e}")
        
        # 2. 构造用户输入
        if context_str:
            system_prompt = """你是一个友好、专业的AI助手。
重要提示：用户的问题基于之前的对话上下文。请仔细阅读提供的上下文信息（包括对话摘要、近期对话和相关历史对话），并基于这些上下文来理解和回答当前问题。
如果用户的问题中有代词（如"它"、"这个"等），请根据上下文判断其具体指代。
请用简洁、准确的语言回答用户的问题。"""
            user_input = f"=== 上下文信息 ===\n{context_str}\n\n=== 当前问题 ===\n{request.message}"
            logger.info(f"[{session_id}] 使用上下文回答")
        else:
            system_prompt = "你是一个友好、专业的AI助手。请用简洁、准确的语言回答用户的问题。"
            user_input = request.message
            logger.info(f"[{session_id}] 无上下文，直接回答")
        
        # 3. 调用LLM
        reply = await llm_client.do_llm(
            model_name=selected_model,
            prompt=system_prompt,
            content=user_input,
            max_tokens=model_config.get("max_tokens", 2000)
        )
        
        logger.info(f"[{session_id}] LLM回复: {reply[:50] if reply else '(空)'}...")
        
        # 4. 保存对话到session
        if request.session_id and manager and reply:
            try:
                from core.models import Message
                await manager.add_message(
                    session_id=session_id,
                    messages=[
                        Message(role="user", content=request.message),
                        Message(role="assistant", content=reply)
                    ]
                )
                logger.info(f"[{session_id}] 对话已保存")
            except Exception as e:
                logger.warning(f"[{session_id}] 保存对话失败: {e}")
        
        return ChatResponse(reply=reply or "", usage={})
        
    except Exception as e:
        logger.error(f"聊天失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@app.post("/debug/context")
async def debug_context(request: dict):
    """调试端点：查看get_message返回的数据和构造的prompt"""
    session_id = request.get("session_id")
    query = request.get("query", "")
    
    if not session_id or not manager:
        return {"error": "需要session_id且manager已初始化"}
    
    # 1. 获取get_message的原始返回
    result = await manager.get_message(session_id=session_id, query=query, top_k=3)
    
    # 2. 提取context
    context_str = ""
    if result.get('code') == 200:
        data = result.get('data', {})
        context_str = data.get('context', '')
    
    # 3. 构造会送给LLM的数据
    selected_model = kllm_config.get('llm', {}).get('selected_model', 'gpt4')
    
    if context_str:
        system_prompt = """你是一个友好、专业的AI助手。
重要提示：用户的问题基于之前的对话上下文。请仔细阅读提供的上下文信息（包括对话摘要、近期对话和相关历史对话），并基于这些上下文来理解和回答当前问题。
如果用户的问题中有代词（如"它"、"这个"等），请根据上下文判断其具体指代。
请用简洁、准确的语言回答用户的问题。"""
        user_input = f"=== 上下文信息 ===\n{context_str}\n\n=== 当前问题 ===\n{query}"
    else:
        system_prompt = "你是一个友好、专业的AI助手。请用简洁、准确的语言回答用户的问题。"
        user_input = query
    
    return {
        "session_id": session_id,
        "query": query,
        "get_message_result": result,
        "context_length": len(context_str),
        "will_use_context": bool(context_str),
        "llm_input": {
            "model": selected_model,
            "system_prompt": system_prompt,
            "user_input": user_input,
            "user_input_length": len(user_input)
        }
    }


@app.get("/chat-ui")
async def chat_page():
    """返回简单聊天页面"""
    html_file = Path(__file__).parent / "frontend" / "chat.html"
    if html_file.exists():
        return FileResponse(html_file)
    raise HTTPException(status_code=404, detail="聊天页面未找到")


async def _process_add_message(
    session_id: str,
    messages: list,
    fault_code: list,
    function_code: list,
    product_code: list,
    user_id: str = None,
):
    """后台任务：异步处理消息添加"""
    try:
        await manager.add_message(
            session_id=session_id,
            messages=messages,
            fault_code=fault_code,
            function_code=function_code,
            product_code=product_code,
            user_id=user_id,
        )
        logger.info(f"后台任务完成：添加消息到会话 {session_id}: {len(messages)} 条")
    except Exception as e:
        logger.error(f"后台任务失败：添加消息到会话 {session_id} 失败: {e}", exc_info=True)


@app.post("/add_message", response_model=AddMessageResponse)
async def add_message(request: AddMessageRequest, background_tasks: BackgroundTasks):
    try:
        # 添加后台任务
        background_tasks.add_task(
            _process_add_message,
            session_id=request.session_id,
            messages=request.messages,
            fault_code=request.fault_code,
            function_code=request.function_code,
            product_code=request.product_code,
            user_id=request.user_id,
        )
        
        logger.info(f"接收到添加消息请求，会话 {request.session_id}: {len(request.messages)} 条，后台处理中...")
        
        # 立即返回成功响应
        return AddMessageResponse(
            code=200,
            message="Message received and processing in background",
            data={"session_id": request.session_id, "status": "processing"},
        )
    
    except Exception as e:
        logger.error(f"添加消息请求失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@app.post("/get_message", response_model=GetMessageResponse)
async def get_message(request: GetMessageRequest):
    try:
        result = await manager.get_message(
            session_id=request.session_id,
            query=request.query,
            top_k=5,
        )
        
        if result["code"] == 404:
            raise HTTPException(status_code=404, detail=result["message"])
        
        logger.info(f"获取会话 {request.session_id} 的上下文")
        
        return GetMessageResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get message: {str(e)}")


@app.get("/sessions")
async def list_sessions():
    sessions = manager.list_sessions()
    return {
        "sessions": sessions,
        "count": len(sessions),
    }


@app.get("/users/{user_id}/sessions")
async def list_user_sessions(user_id: str):
    """获取指定用户的所有会话（需要 Redis 存储才能精确按用户查询）"""
    sessions = manager.list_sessions_by_user(user_id)
    return {
        "user_id": user_id,
        "sessions": sessions,
        "count": len(sessions),
    }


def main():
    parser = argparse.ArgumentParser(description="Session Memory服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8789, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")
    parser.add_argument("--log-level", default="info", help="日志级别")
    
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Session Memory服务器启动")
    logger.info("=" * 60)
    logger.info(f"监听地址: {args.host}:{args.port}")
    logger.info(f"🌐 前端页面: http://localhost:{args.port}/")
    logger.info(f"📚 API文档: http://localhost:{args.port}/docs")
    logger.info(f"💚 健康检查: http://localhost:{args.port}/health")
    logger.info("=" * 60)

    # 根据是否需要reload选择不同的启动方式
    if args.reload:
        # reload模式需要使用字符串路径
        uvicorn.run(
            "app:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level=args.log_level,
        )
    else:
        # 非reload模式直接传入app对象，性能更好
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level,
        )


if __name__ == "__main__":
    main()
