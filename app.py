"""
AI 模拟面试系统 v2.0（多智能体协同版）—— Streamlit 前端

运行方式：streamlit run app.py
"""

import plotly.graph_objects as go
import streamlit as st

from data.resume_loader import (
    get_all_categories,
    get_resume_by_index,
    get_resume_by_job,
    get_resume_list,
)
from db.session_db import init_db, save_interview
from graph.workflow import build_interview_graph
from langchain_core.messages import HumanMessage
from utils.api_client import llm_call

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="AI 模拟面试系统 v2.0",
    page_icon="🤖",
    layout="wide",
)

# 全局样式
st.markdown(
    """
<style>
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.2rem !important; }
    .stMarkdown, .stMarkdown p, p { font-size: 0.95rem !important; }
    .stSelectbox label, .stTextInput label, .stRadio label { font-size: 0.95rem !important; }
    .stButton button { font-size: 0.95rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------- 初始化 ----------
init_db()

if "stage" not in st.session_state:
    st.session_state.stage = "select_job"  # select_job | interview | report
if "graph" not in st.session_state:
    st.session_state.graph = build_interview_graph()
if "state" not in st.session_state:
    st.session_state.state = {}
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "target_job" not in st.session_state:
    st.session_state.target_job = ""


def reset_all():
    """重置所有状态，回到选岗页面。"""
    st.session_state.stage = "select_job"
    st.session_state.state = {}
    st.session_state.resume_text = ""
    st.session_state.target_job = ""


def translate_resume(english_text: str) -> str:
    """调用 LLM 将英文简历翻译为中文。"""
    prompt = f"""请将以下英文简历翻译成中文。要求：
- 保持所有技术术语、公司名、职位名不翻译（或括号注明英文）
- 保持原有的段落结构和换行
- 人名、地名可直接音译
- 数字、日期原样保留

英文简历：
---
{english_text}
---

中文翻译："""

    messages = [
        {"role": "user", "content": prompt},
    ]
    return llm_call(messages, temperature=0.1)


# ========================== 阶段一：选岗 / 上传简历 ==========================
if st.session_state.stage == "select_job":
    st.title("🤖 AI 模拟面试系统 v2.0")
    st.markdown("### 多智能体协同面试评估平台")
    st.markdown("---")

    # 选择简历来源
    resume_source = st.radio(
        "选择简历来源",
        ["📂 上传自己的简历", "🎮 使用模拟简历体验"],
        horizontal=True,
    )

    resume_text = ""
    target_job = ""

    if resume_source == "📂 上传自己的简历":
        st.markdown("#### 方式一：上传 TXT 文件（推荐）")
        uploaded_file = st.file_uploader("选择 .txt 简历文件", type=["txt"])
        if uploaded_file is not None:
            try:
                resume_text = uploaded_file.read().decode("utf-8")
                st.success(f"已读取：{uploaded_file.name}（{len(resume_text)} 字）")
            except Exception:
                st.error("文件编码不是 UTF-8，请用方式二粘贴内容。")

        st.markdown("#### 方式二：直接粘贴简历内容")
        pasted = st.text_area(
            "把简历内容粘贴到这里",
            placeholder="例如：\n姓名：张三\n工作年限：5 年\n技能：Python, Django, PostgreSQL...\n项目经历：\n1. xxx 系统开发...\n2. ...",
            height=200,
        )
        if pasted.strip():
            resume_text = pasted

        st.markdown("#### 目标岗位")
        target_job = st.text_input(
            "输入你面试的目标岗位",
            placeholder="例如：后端开发工程师、数据分析师...",
        )

        # 上传模式下,简历和目标岗位都有内容才能开始
        can_start = bool(resume_text.strip()) and bool(target_job.strip())

    else:
        # 模拟简历模式（真实 Kaggle 数据集，2484 份简历，24 个类别）
        if "categories" not in st.session_state:
            st.session_state.categories = get_all_categories()

        target_job = st.selectbox(
            "第①步：选择目标岗位（共 24 个类别）",
            st.session_state.categories,
            index=None,
            placeholder="点击选择...",
        )

        if target_job:
            resume_list = get_resume_list(target_job)
            total = len(resume_list)
            st.caption(f"该类别共有 **{total}** 份简历")

            # 下拉框选择简历
            options = [f"#{r['index']+1:03d} | {r['preview'][:60]}" for r in resume_list]
            selected_label = st.selectbox(
                f"第②步：选择具体简历（共 {total} 份）",
                options,
                index=None,
                placeholder="点击展开，选择一份简历...",
            )

            if selected_label:
                idx = int(selected_label.split("|")[0].replace("#", "").strip()) - 1
                resume_text = get_resume_by_index(target_job, idx)

                if resume_text:
                    st.success(f"已选择 #{idx+1:03d} 号简历（{len(resume_text)} 字符）")

                    tab_en, tab_cn = st.tabs(["📄 英文原文", "🌐 中文翻译"])
                    with tab_en:
                        with st.container(height=320):
                            st.text(resume_text)
                    with tab_cn:
                        trans_key = f"trans_{target_job}_{idx}"
                        if trans_key not in st.session_state:
                            st.session_state[trans_key] = ""
                        if st.button("🔤 翻译成中文", key=f"trans_btn_{idx}"):
                            with st.spinner("正在调用 AI 翻译..."):
                                st.session_state[trans_key] = translate_resume(resume_text)
                        if st.session_state[trans_key]:
                            with st.container(height=320):
                                st.text(st.session_state[trans_key])
                        else:
                            st.info("点击上方按钮，AI 将自动翻译为中文")
                else:
                    resume_text = ""
            else:
                resume_text = ""

        can_start = bool(target_job) and bool(resume_text.strip())

    # 开始按钮
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 开始面试", type="primary", disabled=(not can_start), use_container_width=True):
            st.session_state.target_job = target_job
            st.session_state.resume_text = resume_text

            initial_state = {
                "resume_text": resume_text,
                "target_job": target_job,
                "candidate_profile": {},
                "messages": [],
                "round_scores": [],
                "final_report": {},
                "current_round": 0,
                "max_rounds": 99,
                "main_question_index": 0,
                "max_main_questions": 5,
                "followup_count": 0,
                "max_followups": 3,
                "next_question_type": "main",
                "end_requested": False,
                "interview_completed": False,
            }

            with st.spinner("正在加载数据集并分析简历，请稍候..."):
                result = st.session_state.graph.invoke(initial_state)
            st.session_state.state = result
            st.session_state.stage = "interview"
            st.rerun()

    st.markdown("---")
    st.caption("💡 系统将使用 AI 多智能体协同工作：简历分析 → 动态提问 → 实时评估 → 综合报告")

# ========================== 阶段二：面试对话 ==========================
elif st.session_state.stage == "interview":
    state = st.session_state.state
    graph = st.session_state.graph

    st.title(f"🎯 面试进行中 —— {st.session_state.target_job}")
    mi = state.get("main_question_index", 0)
    mm = state.get("max_main_questions", 5)
    fc = state.get("followup_count", 0)
    mf = state.get("max_followups", 3)
    qtype = state.get("next_question_type", "main")
    if qtype == "followup":
        st.caption(f"主问题 {mi+1}/{mm} · 追问 {fc}/{mf} ── 回答不够深入，追加细节问题")
    else:
        st.caption(f"主问题 {mi+1}/{mm} ── 开始新的考察方向")

    # 显示对话历史
    chat_container = st.container(height=400)
    with chat_container:
        messages = state.get("messages", [])
        if not messages:
            st.info("正在准备第一个问题...")
        for msg in messages:
            if hasattr(msg, "type"):
                if msg.type == "human":
                    with st.chat_message("user"):
                        st.markdown(msg.content)
                else:
                    with st.chat_message("assistant", avatar="🎙️"):
                        st.markdown(msg.content)

    # 用户输入区域 + 结束按钮
    st.markdown("---")
    col_input, col_end = st.columns([4, 1])
    with col_input:
        user_answer = st.chat_input("输入你的回答...")
    with col_end:
        end_interview = st.button("🛑 结束面试", type="secondary", use_container_width=True)

    if user_answer:
        current_state = dict(st.session_state.state)
        current_state["messages"] = list(current_state.get("messages", [])) + [
            HumanMessage(content=user_answer)
        ]

        with st.spinner("正在评估回答..."):
            result = graph.invoke(current_state)

        st.session_state.state = result

        if result.get("interview_completed", False):
            final_report = result.get("final_report", {})
            total_score = final_report.get("total_score", 0)
            save_interview(
                job_category=st.session_state.target_job,
                resume_text=st.session_state.resume_text,
                final_report=final_report,
                total_score=total_score,
            )
            st.session_state.stage = "report"

        st.rerun()

    if end_interview:
        current_state = dict(st.session_state.state)
        current_state["end_requested"] = True
        # 如果用户还没回答本轮问题，也直接生成报告
        with st.spinner("正在生成最终评估报告..."):
            result = graph.invoke(current_state)

        st.session_state.state = result

        if result.get("interview_completed", False):
            final_report = result.get("final_report", {})
            total_score = final_report.get("total_score", 0)
            save_interview(
                job_category=st.session_state.target_job,
                resume_text=st.session_state.resume_text,
                final_report=final_report,
                total_score=total_score,
            )
            st.session_state.stage = "report"

        st.rerun()

# ========================== 阶段三：报告展示 ==========================
elif st.session_state.stage == "report":
    st.title("📊 面试综合评估报告")
    st.markdown("---")

    final_report = st.session_state.state.get("final_report", {})
    if not final_report:
        st.warning("报告数据为空，请重新开始。")
        if st.button("🔄 重新开始"):
            reset_all()
            st.rerun()
        st.stop()

    total_score = final_report.get("total_score", 0)
    dimensions = final_report.get("dimensions", {})
    strengths = final_report.get("strengths", [])
    weak_points = final_report.get("weak_points", [])
    improvements = final_report.get("improvement_suggestions", [])

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # 总分仪表盘风格展示
        st.metric("综合总分", f"{total_score} / 100")

        # Plotly 雷达图
        if dimensions:
            dim_names = list(dimensions.keys())
            dim_values = [dimensions.get(k, 0) for k in dim_names]

            fig = go.Figure()
            fig.add_trace(
                go.Scatterpolar(
                    r=dim_values + [dim_values[0]],
                    theta=dim_names + [dim_names[0]],
                    fill="toself",
                    name="维度得分",
                    line_color="#636EFA",
                    fillcolor="rgba(99, 110, 250, 0.3)",
                )
            )
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100], showticklabels=True)),
                showlegend=False,
                height=250,
                margin=dict(l=40, r=40, t=30, b=20),
                title=dict(text="能力维度雷达图", font=dict(size=14)),
            )
            st.plotly_chart(fig, use_container_width=True)

        # 柱状图
        if dimensions:
            fig_bar = go.Figure()
            fig_bar.add_trace(
                go.Bar(
                    x=list(dimensions.values()),
                    y=list(dimensions.keys()),
                    orientation="h",
                    marker_color=["#636EFA", "#00CC96", "#AB63FA"],
                    text=[f"{v}" for v in dimensions.values()],
                    textposition="outside",
                )
            )
            fig_bar.update_layout(
                xaxis=dict(range=[0, 100], title="得分"),
                height=180,
                margin=dict(l=20, r=20, t=30, b=20),
                title=dict(text="各维度得分对比", font=dict(size=14)),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        # 文本报告
        if strengths:
            st.subheader("✅ 优势")
            for s in strengths:
                st.markdown(f"- {s}")

        if weak_points:
            st.subheader("⚠️ 薄弱点")
            for w in weak_points:
                st.markdown(f"- {w}")

        if improvements:
            st.subheader("💡 改进建议")
            for imp in improvements:
                st.markdown(f"- {imp}")

    # 每轮详细评分
    round_scores = st.session_state.state.get("round_scores", [])
    if round_scores:
        st.markdown("---")
        st.subheader("📋 各轮次评分明细")
        for i, score in enumerate(round_scores, 1):
            with st.expander(f"第 {i} 轮"):
                c1, c2, c3 = st.columns(3)
                c1.metric("技术深度", f"{score.get('tech_score', 'N/A')}/10")
                c2.metric("沟通表达", f"{score.get('communication_score', 'N/A')}/10")
                c3.metric("逻辑结构", f"{score.get('logic_score', 'N/A')}/10")
                st.caption(score.get("brief_comment", ""))

    st.markdown("---")
    if st.button("🔄 重新开始", type="primary", use_container_width=True):
        reset_all()
        st.rerun()
