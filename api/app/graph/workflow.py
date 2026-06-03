"""
LangGraph 状态图构建 —— 智能提问策略：

  5 个高价值问题为主线。每轮回答评分：
  - 得分 ≥ 70 → 进入下一个主问题
  - 得分 < 70 → 追问细节（最多 3 次），追问得分 ≥ 70 也进入下一主问题
  - 5 个主问题全部覆盖 → 生成最终报告
  - 用户随时可按「结束面试」提前生成报告
"""

from langgraph.graph import END, START, StateGraph

from app.agents import (
    analyze_resume_node,
    ask_question_node,
    evaluate_node,
    final_report_node,
)
from app.graph.state import InterviewState


def _route_entry(state: dict) -> str:
    """入口路由：首次（无画像）→ init，用户已回答 → eval，已完成 → end。"""
    if state.get("interview_completed", False):
        return "end"
    if not state.get("candidate_profile"):
        return "init"
    return "eval"


def _route_after_advance(state: dict) -> str:
    """
    advance 之后的路由：
      "report"   — 所有主问题已完成，或用户主动结束
      "main"     — 下一个是高价值问题
      "followup" — 下一个是细节追问
    """
    if state.get("end_requested", False):
        return "report"
    mi = state.get("main_question_index", 0)
    mm = state.get("max_main_questions", 5)
    if mi >= mm:
        return "report"
    if state.get("next_question_type", "main") == "followup":
        return "followup"
    return "main"


def _advance_question(state: dict) -> dict:
    """
    智能推进节点：读取本轮评分，决定下一步。

    返回更新字段：
      - main_question_index（如晋级）
      - followup_count（加 1 或归 0）
      - next_question_type（"main" 或 "followup"）
    """
    round_scores = state.get("round_scores", [])
    mi = state.get("main_question_index", 0)
    fc = state.get("followup_count", 0)
    mf = state.get("max_followups", 3)
    mm = state.get("max_main_questions", 5)
    end_requested = state.get("end_requested", False)

    if end_requested or mi >= mm:
        return {"next_question_type": "main"}

    # 计算本轮总分（取最近一条评分的三维平均）
    avg = 50.0
    if round_scores:
        last = round_scores[-1]
        avg = (last.get("tech_score", 5) + last.get("communication_score", 5) + last.get("logic_score", 5)) * 10 / 3

    if avg >= 70.0 or fc >= mf:
        # 晋级到下一个主问题
        mi += 1
        fc = 0
        qtype = "main"
    else:
        # 追问细节
        fc += 1
        qtype = "followup"

    return {
        "main_question_index": mi,
        "followup_count": fc,
        "next_question_type": qtype,
    }


def _increment_round(state: dict) -> dict:
    """递增轮次计数。"""
    return {"current_round": state.get("current_round", 0) + 1}


def build_interview_graph() -> StateGraph:
    """
    构建面试工作流 StateGraph。

    流程：
    START → route_entry ──init──→ analyze_resume → inc_round → ask_question → END
              │
              ├──eval──→ evaluate → advance_question
              │                         │
              │              ┌─ main ───┤
              │              ├─ followup┤── inc_round → ask_question → END
              │              └─ report ──→ final_report → END
              │
              └──end───→ END
    """
    builder = StateGraph(InterviewState)

    builder.add_node("analyze_resume", analyze_resume_node)
    builder.add_node("increment_round", _increment_round)
    builder.add_node("ask_question", ask_question_node)
    builder.add_node("evaluate", evaluate_node)
    builder.add_node("advance_question", _advance_question)
    builder.add_node("final_report", final_report_node)

    # 条件入口
    builder.add_conditional_edges(
        START, _route_entry,
        {"init": "analyze_resume", "eval": "evaluate", "end": END},
    )

    # init 路径
    builder.add_edge("analyze_resume", "increment_round")
    builder.add_edge("increment_round", "ask_question")
    builder.add_edge("ask_question", END)

    # eval 路径：评分 → 智能推进 → 路由
    builder.add_edge("evaluate", "advance_question")
    builder.add_conditional_edges(
        "advance_question", _route_after_advance,
        {
            "main": "increment_round",
            "followup": "increment_round",
            "report": "final_report",
        },
    )
    builder.add_edge("final_report", END)

    return builder.compile()
