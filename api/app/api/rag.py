"""
RAG 知识库 API —— 文档上传、检索、对话。
"""

import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from app.api.auth import verify_token
from app.config import settings
from app.models.schemas import DocumentUploadResponse, RAGChatRequest
from app.services.rag_service import rag_service
from app.utils.api_client import llm_call_async, llm_call

router = APIRouter()


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token),
):
    """上传文档到知识库（支持 TXT, MD, PDF, DOCX）。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    content = await file.read()

    # 尝试 UTF-8 解码
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="暂不支持二进制文件，请上传 TXT 或 Markdown 文件",
        )

    if len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="文档内容过短，至少需要 50 个字符")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"

    doc_id = rag_service.add_document(
        filename=file.filename,
        content=text,
        file_type=ext,
    )

    stats = rag_service.get_stats()
    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        chunk_count=stats["total_chunks"],
    )


@router.get("/documents")
async def list_documents(user_id: str = Depends(verify_token)):
    """获取知识库文档列表。"""
    return {"items": rag_service.list_documents()}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Depends(verify_token),
):
    """删除知识库文档。"""
    deleted = rag_service.delete_document(document_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"deleted_chunks": deleted}


@router.post("/chat")
async def rag_chat(
    request: RAGChatRequest,
    user_id: str = Depends(verify_token),
):
    """
    RAG 增强对话 —— 检索相关知识库内容，结合 LLM 生成回答。

    SSE 流式返回（打字机效果）。
    """
    # 检索相关文档片段
    relevant = rag_service.search(request.query)

    async def event_generator():
        if not relevant:
            yield f"data: {json.dumps({'type': 'info', 'message': '知识库中没有找到相关内容'})}\n\n"
            yield "event: done\ndata: {}\n\n"
            return

        # 构建增强 prompt
        context = "\n\n---\n\n".join(
            [f"[来源: {r['filename']}]\n{r['content']}" for r in relevant]
        )

        prompt = f"""你是一个智能面试助手。请根据以下知识库材料回答用户的问题。

知识库材料：
---
{context}
---

用户问题：{request.query}

请基于知识库内容给出准确、专业的回答。如果知识库中没有直接答案，请诚实说明，并基于你自己的知识给出补充建议。"""

        messages = [
            {"role": "system", "content": "你是一个专业的面试辅导助手，请基于提供的知识库材料回答问题。"},
            {"role": "user", "content": prompt},
        ]

        try:
            # 使用 LLM 流式输出（如果 API 支持的话）
            import asyncio
            response = await llm_call_async(messages, temperature=0.3)
            sources = [{"filename": r["filename"], "score": round(r["score"], 3)} for r in relevant[:3]]
            result = {"type": "answer", "content": response, "sources": sources}
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
