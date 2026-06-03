"""
语音面试 WebSocket 端点 —— 实时语音对话。

协议：JSON over WebSocket
- 客户端→服务端：audio_chunk, speech_end, submit_answer, end_interview
- 服务端→客户端：transcript, question_audio, score, interview_complete
"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.auth import verify_token
from app.api.deps import get_db
from app.models.db import Interview

router = APIRouter()


@router.websocket("/interview/{session_id}/voice")
async def voice_interview(websocket: WebSocket, session_id: str):
    """
    语音面试 WebSocket 端点。

    客户端连接时需要传 token 参数：ws://host/ws/interview/{id}/voice?token=jwt
    """
    await websocket.accept()

    try:
        # 验证 token（从查询参数）
        token = websocket.query_params.get("token", "")
        if not token:
            await websocket.send_json({"type": "error", "message": "缺少认证 Token"})
            await websocket.close()
            return

        # 简单 token 验证
        from jose import jwt as jose_jwt
        from app.config import settings
        try:
            payload = jose_jwt.decode(
                token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub", "")
        except Exception:
            await websocket.send_json({"type": "error", "message": "Token 无效"})
            await websocket.close()
            return

        # 发送连接成功
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "语音面试已连接",
        })

        # 主循环 —— 处理客户端消息
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "audio_chunk":
                # 阶段 4 完整版：发送到 ASR 服务
                # 当前返回占位响应
                pass

            elif msg_type == "speech_end":
                # VAD 检测到语音结束 → 发送到 ASR
                # 占位：返回模拟转录
                await websocket.send_json({
                    "type": "transcript",
                    "text": "[语音识别结果将在这里显示]",
                    "is_partial": False,
                })

            elif msg_type == "submit_answer":
                # 用户手动提交答案
                answer_text = data.get("text", "")
                if answer_text:
                    await websocket.send_json({
                        "type": "info",
                        "message": f"收到回答：{answer_text[:50]}...",
                    })

            elif msg_type == "end_interview":
                await websocket.send_json({
                    "type": "interview_complete",
                    "message": "面试已结束",
                })
                break

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"未知消息类型: {msg_type}",
                })

    except WebSocketDisconnect:
        print(f"[INFO] 语音面试 WebSocket 断开: session={session_id}")
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
