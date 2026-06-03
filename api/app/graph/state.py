"""InterviewState 定义 —— LangGraph 共享状态，所有节点通过它传递数据。"""

from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages


class InterviewState(TypedDict):
    """面试工作流的全局状态。"""

    # 简历 & 岗位
    resume_text: str
    target_job: str

    # 简历分析生成的候选人画像
    candidate_profile: dict

    # 对话消息（使用 add_messages 注解保证消息安全追加）
    messages: Annotated[list, add_messages]

    # 每轮的评分记录 [{tech_score, communication_score, logic_score, brief_comment}, ...]
    round_scores: list

    # 最终报告（面试结束后填充）
    final_report: dict

    # 轮次控制
    current_round: int
    max_rounds: int  # 安全上限（默认 99）

    # 智能提问策略
    main_question_index: int      # 当前是第几个高价值问题（0-based）
    max_main_questions: int       # 高价值问题总数（默认 5）
    followup_count: int           # 当前主问题下已追问次数
    max_followups: int            # 每个主问题最多追问次数（默认 3）
    next_question_type: str       # 下一问类型："main" / "followup"

    # 用户主动结束面试
    end_requested: bool

    # 是否已完成面试
    interview_completed: bool
