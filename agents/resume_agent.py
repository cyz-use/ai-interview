"""简历分析 Agent —— 从简历文本中提取结构化候选人画像。"""

import json

from utils.api_client import llm_call

SYSTEM_PROMPT = """你是一位资深的 HR 专家和职业顾问。请根据提供的候选人简历文本，提取出以下结构化信息。

要求：
1. 仔细阅读简历，提取所有技能名称、项目关键词、教育背景、工作年限
2. 根据简历内容与该岗位的相关度，给出 0-100 的匹配度评分
3. 用简洁的话语总结候选人的核心优势（50 字以内）

你必须严格输出 JSON 格式，字段说明：
- skills: 技能名称列表
- years_of_experience: 工作年限（整数）
- education: 最高学历及专业
- project_keywords: 项目关键词/技术栈列表
- match_score: 匹配度评分（0-100 整数）
- summary: 候选人核心优势简述
"""


def analyze_resume_node(state: dict) -> dict:
    """
    分析简历，输出候选人结构化画像。

    从 state 中读取 resume_text 和 target_job，调用 LLM 生成画像，
    将结果存入 candidate_profile 字段。
    """
    resume_text = state.get("resume_text", "")
    target_job = state.get("target_job", "")

    user_prompt = f"""候选人目标岗位：{target_job}

以下是候选人简历文本：
---
{resume_text}
---

请根据以上信息，提取结构化画像并输出 JSON。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = llm_call(messages, temperature=0.3, response_format="json_object")
    try:
        profile = json.loads(response)
    except json.JSONDecodeError:
        profile = {
            "skills": [],
            "years_of_experience": 0,
            "education": "未知",
            "project_keywords": [],
            "match_score": 50,
            "summary": "解析失败",
        }

    return {"candidate_profile": profile}
