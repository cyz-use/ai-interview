"""评估 Agent —— 对每轮回答进行实时多维度评分，面试结束后生成综合报告。"""

import json

from app.utils.api_client import llm_call

ROUND_EVAL_PROMPT = """你是一位经验丰富的技术面试评估专家。请根据候选人在当前轮的回答进行评分。

评分维度（每项 1-10 分）：
- tech_score: 技术深度与准确性
- communication_score: 表达清晰度与沟通能力
- logic_score: 逻辑结构与问题分析能力
- brief_comment: 简短点评（30 字以内）

请严格输出 JSON 格式，只输出 JSON，不要有任何其他文字。"""

FINAL_REPORT_PROMPT = """你是一位资深技术面试评估专家。请根据候选人在整个面试过程中的所有轮次表现，生成一份完整的综合评估报告。

报告需包含以下内容，并严格输出 JSON 格式：
- total_score: 综合总分（1-100）
- dimensions: 包含以下三个维度的评分（每项 1-100）：
  - 技术深度: 体现候选人对技术原理、细节的掌握程度
  - 沟通表达: 体现候选人表达清晰度、结构化沟通能力
  - 问题解决: 体现候选人分析问题、提出解决方案的能力
- weak_points: 薄弱点列表（3-5 条）
- strengths: 优势列表（3-5 条）
- improvement_suggestions: 改进建议列表（3-5 条）

请只输出 JSON，不要有任何额外文字。"""


def evaluate_node(state: dict) -> dict:
    """
    评估节点：对当前轮次的候选人回答进行多维度评分。

    从 state 中读取 messages（取最后一条人类消息作为本轮回答），
    调用 LLM 评分后将结果追加到 round_scores。
    """
    messages = state.get("messages", [])
    round_scores = list(state.get("round_scores", []))

    # 取最后一条人类消息（即候选人本轮回答）
    last_answer = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_answer = msg.content
            break

    if not last_answer:
        # 没有找到回答，跳过评分
        return {"round_scores": round_scores}

    msgs_for_llm = [
        {"role": "system", "content": ROUND_EVAL_PROMPT},
        {"role": "user", "content": f"候选人的本轮回答：\n{last_answer}"},
    ]

    response = llm_call(msgs_for_llm, temperature=0.3, response_format="json_object")
    try:
        score = json.loads(response)
    except json.JSONDecodeError:
        score = {
            "tech_score": 5,
            "communication_score": 5,
            "logic_score": 5,
            "brief_comment": "评分解析失败",
        }

    round_scores.append(score)
    return {"round_scores": round_scores}


def final_report_node(state: dict) -> dict:
    """
    最终报告节点：汇总所有轮次的表现，生成综合评估报告。

    将所有轮次的问答和评分拼接后传给 LLM，生成 final_report。
    同时标记 interview_completed 为 True。
    """
    messages = state.get("messages", [])
    round_scores = state.get("round_scores", [])
    candidate_profile = state.get("candidate_profile", {})
    target_job = state.get("target_job", "")

    # 构建带分数的对话历史
    history_with_scores = "岗位：" + target_job + "\n"
    history_with_scores += "候选人画像：" + json.dumps(candidate_profile, ensure_ascii=False) + "\n\n"
    history_with_scores += "=== 面试过程 ===\n"

    # messages 的排列顺序：面试官(AI)问题 → 候选人(Human)回答 → 面试官问题 → ...
    # 跳过第一条面试官消息（初始欢迎/问题），从候选人的第一条回答开始匹配
    msg_list = list(messages)
    answer_idx = 0
    for i, msg in enumerate(msg_list):
        role = "面试官" if (hasattr(msg, "type") and msg.type != "human") else "候选人"
        if role == "候选人":
            score_info = ""
            if answer_idx < len(round_scores):
                s = round_scores[answer_idx]
                score_info = f" [技术:{s.get('tech_score','N/A')} 沟通:{s.get('communication_score','N/A')} 逻辑:{s.get('logic_score','N/A')}]"
                answer_idx += 1
            history_with_scores += f"{role}: {msg.content}{score_info}\n\n"
        else:
            history_with_scores += f"{role}: {msg.content}\n\n"

    msgs_for_llm = [
        {"role": "system", "content": FINAL_REPORT_PROMPT},
        {"role": "user", "content": f"以下是完整的面试记录，请生成综合评估报告：\n\n{history_with_scores}"},
    ]

    response = llm_call(msgs_for_llm, temperature=0.3, response_format="json_object")
    try:
        report = json.loads(response)
    except json.JSONDecodeError:
        report = {
            "total_score": 60,
            "dimensions": {
                "技术深度": 60,
                "沟通表达": 60,
                "问题解决": 60,
            },
            "weak_points": ["评分解析失败"],
            "strengths": ["暂无"],
            "improvement_suggestions": ["请重新进行面试"],
        }

    return {
        "final_report": report,
        "interview_completed": True,
    }
