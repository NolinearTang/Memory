"""Headroom 压缩服务器

使用 FastAPI 提供压缩服务，支持：
1. 消息压缩接口
2. RAG检索内容压缩
3. 统计信息查询
4. 健康检查

启动服务器：
    python compress_server.py

或指定端口：
    python compress_server.py --port 8080
"""

import argparse
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

try:
    from headroom import compress
except ImportError:
    raise ImportError(
        "请先安装 headroom: pip install headroom-ai[all]"
    )

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Headroom 压缩服务",
    description="基于 Headroom 的消息压缩服务",
    version="1.0.0",
)

# 全局统计
class GlobalStats:
    def __init__(self):
        self.total_requests = 0
        self.total_rag_requests = 0
        self.total_tokens_before = 0
        self.total_tokens_after = 0
        self.total_tokens_saved = 0
        self.start_time = datetime.now()
        self.last_request_time = None
        self.error_count = 0

    def record_success(self, tokens_before: int, tokens_after: int, tokens_saved: int, is_rag: bool = False):
        self.total_requests += 1
        if is_rag:
            self.total_rag_requests += 1
        self.total_tokens_before += tokens_before
        self.total_tokens_after += tokens_after
        self.total_tokens_saved += tokens_saved
        self.last_request_time = datetime.now()

    def record_error(self):
        self.error_count += 1

    def get_stats(self) -> dict:
        uptime = (datetime.now() - self.start_time).total_seconds()
        avg_compression_ratio = (
            self.total_tokens_saved / self.total_tokens_before
            if self.total_tokens_before > 0
            else 0.0
        )
        
        return {
            "total_requests": self.total_requests,
            "total_rag_requests": self.total_rag_requests,
            "total_tokens_before": self.total_tokens_before,
            "total_tokens_after": self.total_tokens_after,
            "total_tokens_saved": self.total_tokens_saved,
            "average_compression_ratio": round(avg_compression_ratio, 3),
            "error_count": self.error_count,
            "uptime_seconds": round(uptime, 2),
            "start_time": self.start_time.isoformat(),
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None,
        }

stats = GlobalStats()


# 请求和响应模型
class CompressRequest(BaseModel):
    """压缩请求"""
    messages: list[dict[str, Any]] = Field(..., description="要压缩的消息列表")
    model: str = Field(default="gpt-4o", description="目标模型名称")
    target_ratio: float | None = Field(default=None, description="目标保留率 (0-1)，None=自动")
    compress_user_messages: bool = Field(default=False, description="是否压缩用户消息")
    protect_recent: int = Field(default=4, description="保护最近 N 条消息不压缩")
    kompress_model: str | None = Field(default=None, description="Kompress 模型ID，'disabled'=禁用ML压缩")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                ],
                "model": "gpt-4o",
                "target_ratio": None,
            }
        }


class CompressResponse(BaseModel):
    """压缩响应"""
    messages: list[dict[str, Any]] = Field(..., description="压缩后的消息")
    tokens_before: int = Field(..., description="压缩前 token 数")
    tokens_after: int = Field(..., description="压缩后 token 数")
    tokens_saved: int = Field(..., description="节省的 token 数")
    compression_ratio: float = Field(..., description="压缩比 (0-1)")
    transforms_applied: list[str] = Field(..., description="应用的压缩算法")
    timestamp: str = Field(..., description="处理时间戳")


# API 端点
@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Headroom 压缩服务",
        "version": "1.0.0",
        "endpoints": {
            "compress": "POST /compress - 压缩消息",
            "compress_rag": "POST /compress-rag - 压缩RAG检索内容",
            "stats": "GET /stats - 查看统计",
            "health": "GET /health - 健康检查",
        },
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_requests": stats.total_requests,
    }


@app.get("/stats")
async def get_stats():
    """获取统计信息"""
    return JSONResponse(content=stats.get_stats())


@app.post("/compress", response_model=CompressResponse)
async def compress_messages(request: CompressRequest):
    """压缩消息"""
    try:
        logger.info(
            f"收到压缩请求: {len(request.messages)} 条消息, model={request.model}"
        )

        # 调用 Headroom 压缩
        result = compress(
            messages=request.messages,
            model=request.model,
            target_ratio=request.target_ratio,
            compress_user_messages=request.compress_user_messages,
            protect_recent=request.protect_recent,
            kompress_model=request.kompress_model,
        )

        # 记录统计
        stats.record_success(
            result.tokens_before,
            result.tokens_after,
            result.tokens_saved,
        )

        logger.info(
            f"压缩完成: {result.tokens_before} → {result.tokens_after} tokens "
            f"(节省 {result.tokens_saved}, {result.compression_ratio:.1%})"
        )

        return CompressResponse(
            messages=result.messages,
            tokens_before=result.tokens_before,
            tokens_after=result.tokens_after,
            tokens_saved=result.tokens_saved,
            compression_ratio=result.compression_ratio,
            transforms_applied=result.transforms_applied,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        stats.record_error()
        logger.error(f"压缩失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"压缩失败: {str(e)}")


class RAGDocument(BaseModel):
    """RAG检索文档"""
    content: str = Field(..., description="文档内容")
    score: float = Field(default=1.0, description="相关性分数 (0-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class CompressRAGRequest(BaseModel):
    """RAG压缩请求"""
    documents: list[RAGDocument] = Field(..., description="检索到的文档列表")
    query: str = Field(..., description="用户查询")
    top_k: int | None = Field(default=None, description="保留前K个文档，None=保留所有")
    min_score: float = Field(default=0.0, description="最低相关性分数阈值")
    target_ratio: float | None = Field(default=0.3, description="每个文档的压缩保留率")
    model: str = Field(default="gpt-4o", description="目标模型")
    preserve_metadata: bool = Field(default=True, description="是否保留元数据")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "content": "Python is a high-level programming language...",
                        "score": 0.95,
                        "metadata": {"source": "doc1.txt", "title": "Python Introduction"}
                    },
                    {
                        "content": "FastAPI is a modern web framework...",
                        "score": 0.85,
                        "metadata": {"source": "doc2.txt", "title": "FastAPI Guide"}
                    }
                ],
                "query": "What is Python?",
                "top_k": 5,
                "min_score": 0.5,
                "target_ratio": 0.3
            }
        }


class CompressRAGResponse(BaseModel):
    """RAG压缩响应"""
    documents: list[dict[str, Any]] = Field(..., description="压缩后的文档")
    original_count: int = Field(..., description="原始文档数量")
    compressed_count: int = Field(..., description="压缩后文档数量")
    tokens_before: int = Field(..., description="压缩前总token数")
    tokens_after: int = Field(..., description="压缩后总token数")
    tokens_saved: int = Field(..., description="节省的token数")
    compression_ratio: float = Field(..., description="总体压缩比")
    timestamp: str = Field(..., description="处理时间戳")


@app.post("/compress-rag", response_model=CompressRAGResponse)
async def compress_rag_documents(request: CompressRAGRequest):
    """压缩RAG检索内容
    
    对检索到的文档进行智能压缩：
    1. 按相关性分数过滤和排序
    2. 保留top-k个最相关的文档
    3. 压缩每个文档的内容
    4. 保留关键元数据
    """
    try:
        logger.info(
            f"收到RAG压缩请求: {len(request.documents)} 个文档, query='{request.query[:50]}...'"
        )

        # 1. 过滤低分文档
        filtered_docs = [
            doc for doc in request.documents
            if doc.score >= request.min_score
        ]
        
        # 2. 按分数排序
        sorted_docs = sorted(filtered_docs, key=lambda x: x.score, reverse=True)
        
        # 3. 保留top-k
        if request.top_k is not None:
            sorted_docs = sorted_docs[:request.top_k]
        
        if not sorted_docs:
            return CompressRAGResponse(
                documents=[],
                original_count=len(request.documents),
                compressed_count=0,
                tokens_before=0,
                tokens_after=0,
                tokens_saved=0,
                compression_ratio=0.0,
                timestamp=datetime.now().isoformat(),
            )
        
        # 4. 压缩每个文档内容
        compressed_docs = []
        total_tokens_before = 0
        total_tokens_after = 0
        
        for doc in sorted_docs:
            # 构造消息格式进行压缩
            messages = [
                {
                    "role": "user",
                    "content": f"Query: {request.query}\n\nDocument:\n{doc.content}"
                }
            ]
            
            # 压缩文档内容
            result = compress(
                messages=messages,
                model=request.model,
                target_ratio=request.target_ratio,
                compress_user_messages=True,
                protect_recent=0,  # RAG内容全部压缩
            )
            
            # 提取压缩后的内容（去掉query部分）
            compressed_content = result.messages[0]["content"]
            if "Document:" in compressed_content:
                compressed_content = compressed_content.split("Document:", 1)[1].strip()
            
            compressed_doc = {
                "content": compressed_content,
                "score": doc.score,
                "original_length": len(doc.content),
                "compressed_length": len(compressed_content),
            }
            
            # 保留元数据
            if request.preserve_metadata and doc.metadata:
                compressed_doc["metadata"] = doc.metadata
            
            compressed_docs.append(compressed_doc)
            total_tokens_before += result.tokens_before
            total_tokens_after += result.tokens_after
        
        total_tokens_saved = total_tokens_before - total_tokens_after
        compression_ratio = total_tokens_saved / total_tokens_before if total_tokens_before > 0 else 0.0
        
        # 记录统计
        stats.record_success(
            total_tokens_before,
            total_tokens_after,
            total_tokens_saved,
            is_rag=True,
        )
        
        logger.info(
            f"RAG压缩完成: {len(request.documents)} → {len(compressed_docs)} 文档, "
            f"{total_tokens_before} → {total_tokens_after} tokens ({compression_ratio:.1%})"
        )
        
        return CompressRAGResponse(
            documents=compressed_docs,
            original_count=len(request.documents),
            compressed_count=len(compressed_docs),
            tokens_before=total_tokens_before,
            tokens_after=total_tokens_after,
            tokens_saved=total_tokens_saved,
            compression_ratio=compression_ratio,
            timestamp=datetime.now().isoformat(),
        )
    
    except Exception as e:
        stats.record_error()
        logger.error(f"RAG压缩失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"RAG压缩失败: {str(e)}")


@app.post("/reset-stats")
async def reset_stats():
    """重置统计信息"""
    global stats
    stats = GlobalStats()
    return {"status": "success", "message": "统计信息已重置"}


def main():
    """启动服务器"""
    parser = argparse.ArgumentParser(description="Headroom 压缩服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8787, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")
    parser.add_argument("--log-level", default="info", help="日志级别")
    
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Headroom 压缩服务器启动")
    logger.info("=" * 60)
    logger.info(f"监听地址: {args.host}:{args.port}")
    logger.info(f"API 文档: http://{args.host}:{args.port}/docs")
    logger.info("=" * 60)

    uvicorn.run(
        "compress_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
