"""ReMe压缩服务器

基于Session的对话压缩和记忆抽取API服务。
使用ReMeLight提供对话管理、压缩、摘要和搜索功能。

启动服务器：
    python -m compress_reme.reme_server

或指定端口：
    python -m compress_reme.reme_server --port 8788
"""

import argparse
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from agentscope.message import Msg
import uvicorn

from ..core.session_manager import SessionManager
from ..core.models import (
    CreateSessionRequest, CreateSessionResponse,
    AddMessagesRequest, AddMessagesResponse,
    CompactRequest, CompactResponse,
    SummaryRequest, SummaryResponse,
    SearchRequest, SearchResponse,
    GetMessagesRequest, GetMessagesResponse,
    SessionStatsResponse, DeleteSessionResponse,
    GlobalStatsResponse,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="ReMe压缩服务",
    description="基于Session的对话压缩和记忆抽取服务",
    version="1.0.0",
)

# 全局Session管理器
session_manager: SessionManager | None = None


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    global session_manager
    
    # 加载 .env 文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("已加载 .env 文件")
    except ImportError:
        logger.warning("python-dotenv 未安装，跳过 .env 文件加载")
    except Exception as e:
        logger.warning(f"加载 .env 文件失败: {e}")
    
    # 创建 SessionManager（会自动从环境变量读取配置）
    session_manager = SessionManager(
        working_dir=".reme_sessions",
    )
    
    # 检查配置
    import os
    if not os.getenv("LLM_API_KEY"):
        logger.warning("⚠️  未设置 LLM_API_KEY 环境变量！")
        logger.warning("   请在 .env 文件中配置或设置环境变量")
        logger.warning("   示例: LLM_API_KEY=your-api-key")
    else:
        logger.info("✅ LLM API 配置已加载")
    
    logger.info("ReMe服务器启动成功")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    global session_manager
    if session_manager:
        await session_manager.shutdown()
    logger.info("ReMe服务器已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "ReMe压缩服务",
        "version": "1.0.0",
        "note": "所有接口都支持自动创建session，无需预先调用create_session",
        "endpoints": {
            "create_session": "POST /sessions - 创建会话（可选，会自动创建）",
            "delete_session": "DELETE /sessions/{session_id} - 删除会话",
            "add_messages": "POST /sessions/{session_id}/messages - 添加消息（自动创建session）",
            "get_messages": "GET /sessions/{session_id}/messages - 获取消息（自动创建session）",
            "compact": "POST /sessions/{session_id}/compact - 压缩对话（自动创建session）",
            "summary": "POST /sessions/{session_id}/summary - 生成摘要（自动创建session）",
            "search": "POST /sessions/{session_id}/search - 搜索记忆（自动创建session）",
            "stats": "GET /sessions/{session_id}/stats - 会话统计（自动创建session）",
            "global_stats": "GET /stats - 全局统计",
            "list_sessions": "GET /sessions - 列出所有会话",
        },
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions": len(session_manager.sessions) if session_manager else 0,
    }


@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """创建新会话"""
    try:
        await session_manager.create_session(
            session_id=request.session_id,
            llm_config=request.llm_config,
            embedding_config=request.embedding_config,
        )
        
        logger.info(f"创建会话: {request.session_id}")
        
        return CreateSessionResponse(
            session_id=request.session_id,
            status="success",
            message=f"Session {request.session_id} created successfully",
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建会话失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = await session_manager.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        logger.info(f"删除会话: {session_id}")
        
        return DeleteSessionResponse(
            session_id=session_id,
            status="success",
            message=f"Session {session_id} deleted successfully",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@app.get("/sessions")
async def list_sessions():
    """列出所有会话"""
    return {
        "sessions": session_manager.list_sessions(),
        "count": len(session_manager.sessions),
    }


async def get_or_create_session(session_id: str, llm_config: dict | None = None, embedding_config: dict | None = None):
    """获取或自动创建会话
    
    Args:
        session_id: 会话ID
        llm_config: LLM配置（可选）
        embedding_config: Embedding配置（可选）
    
    Returns:
        Session对象
    """
    try:
        return session_manager.get_session(session_id)
    except KeyError:
        # Session不存在，自动创建
        logger.info(f"会话 {session_id} 不存在，自动创建")
        await session_manager.create_session(
            session_id=session_id,
            llm_config=llm_config,
            embedding_config=embedding_config,
        )
        return session_manager.get_session(session_id)


@app.post("/sessions/{session_id}/messages", response_model=AddMessagesResponse)
async def add_messages(session_id: str, request: AddMessagesRequest):
    """添加消息到会话（如果会话不存在会自动创建）"""
    try:
        session = await get_or_create_session(session_id)
        
        # 转换为Msg对象
        msgs = [
            Msg(
                name=msg.name or msg.role,  # 如果没有指定name，使用role
                role=msg.role,
                content=msg.content,
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **msg.metadata,
            )
            for msg in request.messages
        ]
        
        session.add_messages(msgs)
        
        logger.info(f"会话 {session_id} 添加 {len(msgs)} 条消息")
        
        return AddMessagesResponse(
            session_id=session_id,
            message_count=len(msgs),
            total_messages=len(session.messages),
        )
    
    except Exception as e:
        logger.error(f"添加消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add messages: {str(e)}")


@app.get("/sessions/{session_id}/messages", response_model=GetMessagesResponse)
async def get_messages(session_id: str, limit: int | None = None):
    """获取会话消息（如果会话不存在会自动创建）"""
    try:
        session = await get_or_create_session(session_id)
        
        messages = session.messages
        if limit is not None:
            messages = messages[-limit:]
        
        # 转换为字典
        msg_dicts = [
            {
                "name": msg.name,
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.metadata if hasattr(msg, 'metadata') else {},
            }
            for msg in messages
        ]
        
        return GetMessagesResponse(
            session_id=session_id,
            messages=msg_dicts,
            total_count=len(session.messages),
        )
    
    except Exception as e:
        logger.error(f"获取消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@app.post("/sessions/{session_id}/compact", response_model=CompactResponse)
async def compact_conversation(session_id: str, request: CompactRequest):
    """压缩对话（如果会话不存在会自动创建）"""
    try:
        session = await get_or_create_session(session_id)
        reme = session.reme
        
        # 获取当前token计数
        token_counter = reme.get_token_counter()
        tokens_before = sum(token_counter.get_num_tokens(msg.content or "") for msg in session.messages)
        
        # 根据类型执行压缩
        if request.compact_type == "tool_result" or request.compact_type == "auto":
            # 压缩tool result
            session.messages = await reme.compact_tool_result(session.messages)
        
        if request.compact_type == "memory" or request.compact_type == "auto":
            # 压缩记忆
            threshold = request.threshold or 100000
            compact_result = await reme.compact_memory(
                messages=session.messages,
                memory_compact_threshold=threshold,
            )
            
            if isinstance(compact_result, dict):
                session.messages = compact_result.get("history_compact", session.messages)
        
        # 计算压缩后token数
        tokens_after = sum(token_counter.get_num_tokens(msg.content or "") for msg in session.messages)
        tokens_saved = tokens_before - tokens_after
        compression_ratio = tokens_saved / tokens_before if tokens_before > 0 else 0.0
        
        # 更新统计
        session.total_tokens = tokens_after
        session.tokens_saved += tokens_saved
        session.update_active()
        
        logger.info(
            f"会话 {session_id} 压缩完成: {tokens_before} → {tokens_after} tokens "
            f"({compression_ratio:.1%})"
        )
        
        return CompactResponse(
            session_id=session_id,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            tokens_saved=tokens_saved,
            compression_ratio=compression_ratio,
            compact_type=request.compact_type,
        )
    
    except Exception as e:
        logger.error(f"压缩失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to compact: {str(e)}")


@app.post("/sessions/{session_id}/summary", response_model=SummaryResponse)
async def summary_conversation(session_id: str, request: SummaryRequest):
    """生成对话摘要（如果会话不存在会自动创建）"""
    try:
        session = await get_or_create_session(session_id)
        reme = session.reme
        
        # 获取token计数
        token_counter = reme.get_token_counter()
        tokens_before = sum(token_counter.get_num_tokens(msg.content or "") for msg in session.messages)
        
        # 生成摘要
        summary_result = await reme.summary_memory(
            messages=session.messages,
        )
        
        summary_text = ""
        if isinstance(summary_result, dict):
            summary_text = summary_result.get("summary", "")
        elif isinstance(summary_result, str):
            summary_text = summary_result
        
        tokens_after = token_counter.get_num_tokens(summary_text)
        
        session.update_active()
        
        logger.info(f"会话 {session_id} 生成摘要: {len(summary_text)} 字符")
        
        return SummaryResponse(
            session_id=session_id,
            summary=summary_text,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            is_background=request.background,
        )
    
    except Exception as e:
        logger.error(f"生成摘要失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@app.post("/sessions/{session_id}/search", response_model=SearchResponse)
async def search_memory(session_id: str, request: SearchRequest):
    """搜索记忆（如果会话不存在会自动创建）"""
    try:
        session = await get_or_create_session(session_id)
        reme = session.reme
        
        # 执行搜索
        search_result = await reme.memory_search(
            query=request.query,
            max_results=request.max_results,
            min_score=request.min_score,
        )
        
        # 解析搜索结果
        results = []
        if hasattr(search_result, 'content'):
            # ToolResponse格式
            results = search_result.content if isinstance(search_result.content, list) else [{"content": search_result.content}]
        elif isinstance(search_result, list):
            results = search_result
        
        session.update_active()
        
        logger.info(f"会话 {session_id} 搜索: '{request.query}', 找到 {len(results)} 个结果")
        
        return SearchResponse(
            session_id=session_id,
            query=request.query,
            results=results,
            result_count=len(results),
        )
    
    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search: {str(e)}")


@app.get("/sessions/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(session_id: str):
    """获取会话统计（如果会话不存在会自动创建）"""
    try:
        session = await get_or_create_session(session_id)
        stats = session.get_stats()
        
        return SessionStatsResponse(**stats)
    
    except Exception as e:
        logger.error(f"获取统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.get("/stats", response_model=GlobalStatsResponse)
async def get_global_stats():
    """获取全局统计"""
    try:
        stats = session_manager.get_global_stats()
        return GlobalStatsResponse(**stats)
    
    except Exception as e:
        logger.error(f"获取全局统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get global stats: {str(e)}")


def main():
    """启动服务器"""
    parser = argparse.ArgumentParser(description="ReMe压缩服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8788, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")
    parser.add_argument("--log-level", default="info", help="日志级别")
    
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("ReMe压缩服务器启动")
    logger.info("=" * 60)
    logger.info(f"监听地址: {args.host}:{args.port}")
    logger.info(f"API 文档: http://{args.host}:{args.port}/docs")
    logger.info("=" * 60)

    uvicorn.run(
        "compress_reme.reme_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
