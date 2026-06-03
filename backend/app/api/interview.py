"""
面试 API —— 核心面试流程端点，支持 SSE 流式响应。

数据库持久化：面试会话保存在 Interview 表中，支持断线恢复。
"""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.auth import verify_token
from app.api.deps import get_db
from app.models.db import Interview, InterviewRound, User
from app.models.schemas import (
    AnswerRequest,
    CandidateProfile,
    InterviewHistoryResponse,
    InterviewSessionResponse,
    StartInterviewRequest,
    StartInterviewResponse,
)
from app.services.interview_service import interview_service

router = APIRouter()


def _state_to_json(state: dict) -> str:
    """将 InterviewState 序列化为 JSON（处理消息对象）。"""
    safe = dict(state)
    # 将 LangChain 消息对象转为可序列化格式
    messages = safe.get("messages", [])
    safe["messages"] = [
        {"type": getattr(m, "type", "ai"), "content": getattr(m, "content", str(m))}
        for m in messages
    ]
    return json.dumps(safe, ensure_ascii=False, default=str)


def _json_to_state(json_str: str) -> dict:
    """从 JSON 恢复 InterviewState。"""
    state = json.loads(json_str)
    # 消息保持为字典格式，LangGraph 可以处理
    return state


# ========== 端点 ==========


@router.post("/start")
async def start_interview(
    request: StartInterviewRequest,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    开始新面试 —— 分析简历并返回第一个问题。
    非流式版本，返回 JSON。
    """
    # 检查试用配额
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.subscription_tier == "free" and user.trial_interviews_used >= user.max_trial_interviews:
        raise HTTPException(
            status_code=402,
            detail=f"试用次数已用完（{user.trial_interviews_used}/{user.max_trial_interviews}），请升级会员继续使用",
        )

    session_id = str(uuid4())
    first_question = ""
    candidate_profile = {}
    state = None

    async for sse_event in interview_service.start_interview(
        request.resume_text, request.target_job
    ):
        for line in sse_event.split("\n"):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if data.get("node") == "ask_question":
                        first_question = data.get("question", "")
                    if data.get("node") == "analyze_resume":
                        candidate_profile = data.get("candidate_profile", {})
                except json.JSONDecodeError:
                    pass

    # 构建初始状态并持久化
    initial_state = {
        "resume_text": request.resume_text,
        "target_job": request.target_job,
        "candidate_profile": candidate_profile,
        "messages": [],
        "round_scores": [],
        "final_report": {},
        "current_round": 1,
        "max_rounds": 99,
        "main_question_index": 0,
        "max_main_questions": 5,
        "followup_count": 0,
        "max_followups": 3,
        "next_question_type": "main",
        "end_requested": False,
        "interview_completed": False,
    }

    interview = Interview(
        id=session_id,
        user_id=user_id,
        target_job=request.target_job,
        candidate_profile_json=json.dumps(candidate_profile, ensure_ascii=False),
        state_snapshot_json=_state_to_json(initial_state),
        status="IN_PROGRESS",
    )
    db.add(interview)

    # 递增试用次数
    if user and user.subscription_tier == "free":
        user.trial_interviews_used += 1
    db.commit()

    return StartInterviewResponse(
        session_id=session_id,
        first_question=first_question or "请简单介绍一下你自己和你的技术背景。",
        candidate_profile=candidate_profile,
    )


@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    request: AnswerRequest,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """提交回答 —— SSE 流式返回评分、追问、下一题。"""
    # 从数据库恢复状态
    interview = db.query(Interview).filter(
        Interview.id == session_id, Interview.user_id == user_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="会话不存在")
    if interview.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="面试已完成")

    state = _json_to_state(interview.state_snapshot_json or "{}")

    # 保存本轮问题文本（用于记录到 interview_rounds）
    last_question = ""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, dict) and msg.get("type") != "human":
            last_question = msg.get("content", "")
            break

    async def event_generator():
        nonlocal state

        async for sse_event in interview_service.submit_answer(state, request.answer):
            # 解析事件，更新状态
            for line in sse_event.split("\n"):
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        node = data.get("node", "")

                        if node == "evaluate":
                            state["round_scores"] = data.get("round_scores", [])
                            # 保存本轮评分到数据库
                            scores = data.get("round_scores", [])
                            if scores:
                                last_score = scores[-1]
                                round_num = state.get("current_round", 0)
                                qtype = state.get("next_question_type", "main")
                                mi = state.get("main_question_index", 0)
                                round_record = InterviewRound(
                                    interview_id=session_id,
                                    round_number=round_num,
                                    question_type=qtype,
                                    main_topic=str(mi),
                                    question_text=last_question,
                                    answer_text=request.answer,
                                    tech_score=last_score.get("tech_score"),
                                    communication_score=last_score.get("communication_score"),
                                    logic_score=last_score.get("logic_score"),
                                    brief_comment=last_score.get("brief_comment", ""),
                                )
                                db.add(round_record)

                        elif node == "advance_question":
                            state["next_question_type"] = data.get("next_question_type", "main")
                            state["main_question_index"] = data.get("main_question_index", 0)
                            state["followup_count"] = data.get("followup_count", 0)

                        elif node == "final_report":
                            state["final_report"] = data.get("final_report", {})
                            state["interview_completed"] = True

                        elif node == "increment_round":
                            state["current_round"] = data.get("current_round", 0)

                        elif node == "ask_question":
                            messages = data.get("question", "")
                            if messages:
                                state["messages"] = state.get("messages", []) + [
                                    {"type": "ai", "content": messages}
                                ]

                    except json.JSONDecodeError:
                        pass

            yield sse_event

        # SSE 结束后持久化最终状态
        interview.state_snapshot_json = _state_to_json(state)
        if state.get("interview_completed"):
            interview.status = "COMPLETED"
            interview.completed_at = datetime.utcnow()
            report = state.get("final_report", {})
            interview.total_score = report.get("total_score", 0)
            interview.final_report_json = json.dumps(report, ensure_ascii=False)
        interview.main_question_index = state.get("main_question_index", 0)
        interview.followup_count = state.get("followup_count", 0)
        interview.current_round = state.get("current_round", 0)
        db.commit()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{session_id}/end")
async def end_interview(
    session_id: str,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """提前结束面试 —— SSE 流式返回最终报告。"""
    interview = db.query(Interview).filter(
        Interview.id == session_id, Interview.user_id == user_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="会话不存在")

    state = _json_to_state(interview.state_snapshot_json or "{}")

    async def event_generator():
        nonlocal state
        async for sse_event in interview_service.end_interview(state):
            for line in sse_event.split("\n"):
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("node") == "final_report":
                            state["final_report"] = data.get("final_report", {})
                            state["interview_completed"] = True
                    except json.JSONDecodeError:
                        pass
            yield sse_event

        # 持久化
        interview.state_snapshot_json = _state_to_json(state)
        interview.status = "COMPLETED"
        interview.completed_at = datetime.utcnow()
        report = state.get("final_report", {})
        interview.total_score = report.get("total_score", 0)
        interview.final_report_json = json.dumps(report, ensure_ascii=False)
        db.commit()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{session_id}/report")
async def get_report(
    session_id: str,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """获取面试报告。"""
    interview = db.query(Interview).filter(
        Interview.id == session_id, Interview.user_id == user_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="会话不存在")
    if not interview.final_report_json:
        raise HTTPException(status_code=400, detail="面试尚未完成")

    return json.loads(interview.final_report_json)


@router.get("/history", response_model=InterviewHistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """获取面试历史列表。"""
    query = db.query(Interview).filter(Interview.user_id == user_id)
    total = query.count()

    interviews = (
        query.order_by(Interview.started_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = [
        InterviewSessionResponse(
            session_id=UUID(interview.id),
            target_job=interview.target_job,
            status=interview.status,
            total_score=interview.total_score,
            started_at=interview.started_at,
            completed_at=interview.completed_at,
        )
        for interview in interviews
    ]

    return InterviewHistoryResponse(items=items, total=total, page=page, size=size)
