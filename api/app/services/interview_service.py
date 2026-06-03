"""
面试服务层 —— 封装 LangGraph 工作流，提供 SSE 流式接口。

核心设计：
- 使用 LangGraph 的 astream() 方法获取每个节点的输出
- 将节点输出格式化为 SSE 事件流
- 支持完整面试流程：start → answer → end（带断线恢复）
"""

import json
from typing import AsyncGenerator, Optional
from uuid import UUID, uuid4

from langchain_core.messages import HumanMessage

from app.graph.workflow import build_interview_graph
from app.config import settings


class InterviewService:
    """面试服务 —— 管理 LangGraph 工作流实例和 SSE 流。"""

    def __init__(self):
        self.graph = build_interview_graph()

    def _make_initial_state(
        self, resume_text: str, target_job: str
    ) -> dict:
        """构建初始 InterviewState。"""
        return {
            "resume_text": resume_text,
            "target_job": target_job,
            "candidate_profile": {},
            "messages": [],
            "round_scores": [],
            "final_report": {},
            "current_round": 0,
            "max_rounds": 99,
            "main_question_index": 0,
            "max_main_questions": settings.max_main_questions,
            "followup_count": 0,
            "max_followups": settings.max_followups_per_question,
            "next_question_type": "main",
            "end_requested": False,
            "interview_completed": False,
        }

    def _format_sse(self, event: str, data: dict) -> str:
        """格式化为 SSE 消息。"""
        json_data = json.dumps(data, ensure_ascii=False, default=str)
        return f"event: {event}\ndata: {json_data}\n\n"

    def _state_to_event(self, node_name: str, node_output: dict) -> dict:
        """将 LangGraph 节点输出转换为前端事件。"""
        event = {
            "node": node_name,
            "status": node_name,
        }

        if node_name == "analyze_resume":
            event["status"] = "分析简历中..."
            event["candidate_profile"] = node_output.get("candidate_profile", {})

        elif node_name == "ask_question":
            messages = node_output.get("messages", [])
            if messages:
                event["question"] = messages[-1].content
            event["status"] = "提问中..."

        elif node_name == "evaluate":
            scores = node_output.get("round_scores", [])
            event["round_scores"] = scores
            event["status"] = "评估回答中..."

        elif node_name == "advance_question":
            event["next_question_type"] = node_output.get("next_question_type", "main")
            event["main_question_index"] = node_output.get("main_question_index", 0)
            event["followup_count"] = node_output.get("followup_count", 0)
            event["status"] = "智能推进中..."

        elif node_name == "final_report":
            event["interview_completed"] = True
            event["final_report"] = node_output.get("final_report", {})
            event["status"] = "生成报告中..."

        elif node_name == "increment_round":
            event["current_round"] = node_output.get("current_round", 0)
            event["status"] = "进入下一轮..."

        return event

    async def start_interview(
        self, resume_text: str, target_job: str
    ) -> AsyncGenerator[str, None]:
        """
        启动面试 —— 执行 init 路径：analyze_resume → increment_round → ask_question。

        Yields:
            SSE 格式字符串，每个节点完成时发送一个事件。
        """
        initial_state = self._make_initial_state(resume_text, target_job)

        try:
            async for chunk in self.graph.astream(
                initial_state,
                stream_mode="updates",
            ):
                # chunk 格式: {node_name: {key: value, ...}}
                for node_name, node_output in chunk.items():
                    event_data = self._state_to_event(node_name, node_output)
                    yield self._format_sse("node_update", event_data)

            yield self._format_sse("done", {"interview_completed": False})

        except Exception as e:
            yield self._format_sse("error", {"message": f"面试启动失败: {str(e)}"})

    async def submit_answer(
        self, current_state: dict, answer: str
    ) -> AsyncGenerator[str, None]:
        """
        提交回答 —— 执行 eval 路径：evaluate → advance_question → (main/followup → increment_round → ask_question) | (report → final_report)。

        参数:
            current_state: 当前完整的 InterviewState 字典
            answer: 用户的最新回答

        Yields:
            SSE 格式字符串。
        """
        # 追加用户回答到消息列表
        updated_state = dict(current_state)
        updated_state["messages"] = list(updated_state.get("messages", [])) + [
            HumanMessage(content=answer)
        ]

        try:
            completed = False
            async for chunk in self.graph.astream(
                updated_state,
                stream_mode="updates",
            ):
                for node_name, node_output in chunk.items():
                    event_data = self._state_to_event(node_name, node_output)
                    yield self._format_sse("node_update", event_data)

                    if event_data.get("interview_completed"):
                        completed = True

            yield self._format_sse(
                "done",
                {"interview_completed": completed},
            )

        except Exception as e:
            yield self._format_sse("error", {"message": f"处理回答失败: {str(e)}"})

    async def end_interview(
        self, current_state: dict
    ) -> AsyncGenerator[str, None]:
        """
        提前结束面试 —— 强制进入 final_report 节点。

        参数:
            current_state: 当前完整的 InterviewState 字典

        Yields:
            SSE 格式字符串。
        """
        updated_state = dict(current_state)
        updated_state["end_requested"] = True

        try:
            async for chunk in self.graph.astream(
                updated_state,
                stream_mode="updates",
            ):
                for node_name, node_output in chunk.items():
                    event_data = self._state_to_event(node_name, node_output)
                    yield self._format_sse("node_update", event_data)

            yield self._format_sse(
                "done",
                {"interview_completed": True},
            )

        except Exception as e:
            yield self._format_sse("error", {"message": f"结束面试失败: {str(e)}"})


# 全局单例
interview_service = InterviewService()
