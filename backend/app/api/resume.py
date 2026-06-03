"""
简历 API —— 上传、Demo 数据集浏览、分析状态查询。
"""

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.auth import verify_token
from app.api.deps import get_db
from app.data.resume_loader import (
    get_all_categories,
    get_resume_by_index,
    get_resume_list,
)
from app.models.db import Resume
from app.models.schemas import (
    DemoResumeDetail,
    DemoResumeItem,
    ResumeListItem,
    ResumeStatusResponse,
    ResumeUploadResponse,
)

router = APIRouter()


# =========================== Demo 简历数据集 ===========================


@router.get("/demo/categories")
async def demo_categories():
    """返回 Kaggle 数据集的 24 个岗位类别。"""
    return {"categories": get_all_categories()}


@router.get("/demo/list")
async def demo_resume_list(category: str):
    """返回某个岗位类别下的所有简历摘要。"""
    resume_list = get_resume_list(category)
    return {
        "items": [
            DemoResumeItem(
                index=r["index"],
                preview=r["preview"],
                length=r["length"],
            )
            for r in resume_list
        ],
        "total": len(resume_list),
    }


@router.get("/demo/{category}/{index}")
async def demo_resume_detail(category: str, index: int):
    """返回某个岗位类别下指定索引的简历全文。"""
    text = get_resume_by_index(category, index)
    if not text:
        raise HTTPException(status_code=404, detail="简历不存在")
    return DemoResumeDetail(text=text)


# =========================== 简历上传 ===========================


def _compute_hash(content: bytes) -> str:
    """计算内容的 SHA-256 哈希。"""
    return hashlib.sha256(content).hexdigest()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """上传简历文件，支持 TXT（阶段 5 扩展 PDF/DOCX 等）。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    content = await file.read()

    # 尝试 UTF-8 解码
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="文件编码不是 UTF-8，暂仅支持 TXT 文本文件。",
        )

    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="简历内容过短，至少需要 10 个字符")

    # 去重检查
    content_hash = _compute_hash(content)
    existing = (
        db.query(Resume)
        .filter(Resume.user_id == user_id, Resume.content_hash == content_hash)
        .first()
    )
    if existing:
        return ResumeUploadResponse(
            resume_id=uuid.UUID(existing.id),
            filename=existing.filename,
            status=existing.analysis_status,
        )

    # 确定文件类型
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"

    resume = Resume(
        user_id=user_id,
        filename=file.filename,
        original_text=text,
        file_type=ext,
        content_hash=content_hash,
        file_size_bytes=len(content),
        analysis_status="COMPLETED",  # TXT 立即可用
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(
        resume_id=uuid.UUID(resume.id),
        filename=resume.filename,
        status=resume.analysis_status,
    )


@router.get("/list")
async def list_resumes(
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有简历。"""
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return {
        "items": [
            ResumeListItem(
                id=uuid.UUID(r.id),
                filename=r.filename,
                created_at=r.created_at,
                status=r.analysis_status,
            )
            for r in resumes
        ],
        "total": len(resumes),
    }


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """获取简历详情和文本。"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == user_id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    return {
        "resume_id": str(resume.id),
        "filename": resume.filename,
        "text": resume.original_text,
        "status": resume.analysis_status,
        "file_type": resume.file_type,
    }


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """删除简历。"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == user_id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    db.delete(resume)
    db.commit()
    return {"message": "已删除"}
