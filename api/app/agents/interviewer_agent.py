"""面试官 Agent —— 支持主问题（高价值）和细节追问两种模式。

v3.0：支持 RAG 知识库增强出题（如果知识库有相关内容，会注入到出题 prompt 中）。
"""

from langchain_core.messages import AIMessage

from app.utils.api_client import llm_call

# 5 个高价值问题方向（按 main_question_index 分配）
_MAIN_TOPICS = [
    "技术深度：深挖候选人简历中核心技能的底层原理、最佳实践、常见陷阱",
    "项目经验：追问最有代表性的项目，了解架构决策、权衡取舍、实际产出",
    "问题解决：考察面对模糊需求或线上故障时的分析思路和解决过程",
    "系统设计：评估候选人从全局视角设计可扩展系统的能力",
    "协作与成长：了解团队协作、冲突处理、技术成长和职业规划",
]

MAIN_SYSTEM_PROMPT = """你是一位资深技术面试官。你的任务是提出一个高价值面试问题。

出题约束：
- 每次只问一个问题，直接输出问题，不要任何前缀解释
- 问题必须具体，结合候选人的简历和岗位，不能是泛泛的"说说你对XX的理解"
- 问题应该是开放式的，让候选人有发挥空间
- 不要重复之前已经问过的内容
"""

FOLLOWUP_SYSTEM_PROMPT = """你是一位资深技术面试官。候选人上一轮的回答不够深入，你需要追问细节。

追问原则：
- 每次只问一个问题，直接输出问题，不要解释
- 针对候选人上一轮回答中的具体技术点、数据、方案深入追问
- 可以追问：为什么选择这个方案？有什么替代方案？具体怎么实现的？遇到过什么坑？
- 语气保持专业但略带引导性，帮助候选人展现真实水平
"""


def ask_question_node(state: dict) -> dict:
    """根据 next_question_type 生成主问题或追问。"""
    profile = state.get("candidate_profile", {})
    target_job = state.get("target_job", "")
    current_round = state.get("current_round", 0)
    messages = state.get("messages", [])
    qtype = state.get("next_question_type", "main")
    mi = state.get("main_question_index", 0)
    fc = state.get("followup_count", 0)

    # 构建对话历史
    history_text = ""
    for msg in messages:
        role = "候选人" if hasattr(msg, "type") and msg.type == "human" else "面试官"
        history_text += f"{role}: {msg.content}\n"

    if qtype == "followup":
        # 细节追问
        system_prompt = FOLLOWUP_SYSTEM_PROMPT
        topic_hint = ""
        user_prompt = f"""目标岗位：{target_job}
候选人画像：
{profile}

对话历史（重点看最后一轮候选人的回答）：
{history_text}

候选人对上一问的回答不够深入（第 {fc} 次追问），请提出一个尖锐的细节追问："""
    else:
        # 高价值主问题
        topic_idx = min(mi, len(_MAIN_TOPICS) - 1)
        topic_hint = _MAIN_TOPICS[topic_idx]
        system_prompt = MAIN_SYSTEM_PROMPT
        user_prompt = f"""目标岗位：{target_job}
候选人画像：
{profile}

当前是第 {current_round} 轮面试，第 {mi + 1}/5 个核心考察方向。

本方向主题：{topic_hint}

对话历史：
{history_text if history_text else "（尚未开始对话）"}

请根据以上信息，围绕「{topic_hint}」提出一个高质量面试问题："""

    msgs_for_llm = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # RAG 增强：从知识库检索相关面试材料
    try:
        from app.services.rag_service import rag_service
        search_query = f"{target_job} {topic_hint} 面试题"
        kb_results = rag_service.search(search_query, top_k=3, threshold=0.3)
        if kb_results:
            kb_context = "\n".join([r["content"][:300] for r in kb_results])
            rag_hint = f"\n\n【参考知识库材料，用于提升出题质量，不要直接复制】：\n{kb_context}"
            msgs_for_llm[1]["content"] += rag_hint
    except Exception:
        pass  # RAG 不可用时静默跳过

    question = llm_call(msgs_for_llm, temperature=0.8)
    return {"messages": [AIMessage(content=question)]}
