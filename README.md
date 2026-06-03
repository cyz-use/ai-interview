# AI 面试系统 v3.0

基于 **FastAPI + LangGraph + React** 的商用级 AI 模拟面试平台。三个 AI Agent 协同工作，支持自适应追问、RAG 知识库增强、语音面试和 Docker 一键部署。

## 与 Snailclimb/interview-guide 的对比

| 能力 | Snailclimb/interview-guide | 本系统 (v3.0) |
|------|---------------------------|---------------|
| Agent 架构 | 传统分层，无 Agent | **LangGraph 三 Agent 协同** |
| 自适应追问 | 固定配置式 | **评分驱动智能追问** |
| Demo 体验 | 必须上传简历 | **2484 份真实简历即开即用** |
| 知识库增强 | 无 | **RAG 检索增强出题** |
| 语音面试 | 有 | 有 |
| 流式响应 | 有 | 有 (SSE) |
| 后端语言 | Java | Python（AI 生态更好） |
| 前端 | React | React |

## 快速开始

### 方式一：Docker 一键部署（推荐）

```bash
# 1. 克隆项目
git clone <repo-url> && cd ai_interview_v2

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY

# 3. 启动所有服务
docker-compose up -d

# 4. 打开浏览器
# 前端: http://localhost:5173
# API 文档: http://localhost:8000/docs
```

### 方式二：本地开发

**后端：**

```bash
cd backend
pip install -r requirements.txt
cp ../.env .env  # 或者手动创建 backend/.env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:5173`。

## 项目结构

```
ai_interview_v2/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── config.py                # 配置管理
│   │   ├── api/                     # REST + WebSocket 端点
│   │   │   ├── auth.py              # 认证（注册/登录/JWT）
│   │   │   ├── interview.py         # 面试核心（SSE 流式）
│   │   │   ├── resume.py            # 简历管理 + Demo 数据集
│   │   │   ├── rag.py               # RAG 知识库
│   │   │   └── voice.py             # WebSocket 语音面试
│   │   ├── models/
│   │   │   ├── schemas.py           # Pydantic 请求/响应模型
│   │   │   └── db.py                # SQLAlchemy ORM
│   │   ├── services/
│   │   │   ├── interview_service.py # LangGraph 工作流编排
│   │   │   ├── rag_service.py       # RAG 检索增强
│   │   │   └── voice_service.py     # 语音处理
│   │   ├── agents/                  # 三个 AI Agent
│   │   │   ├── resume_agent.py      # 简历分析
│   │   │   ├── interviewer_agent.py # 面试官（含 RAG 增强）
│   │   │   └── evaluator_agent.py   # 评估
│   │   ├── graph/                   # LangGraph 状态图
│   │   │   ├── state.py             # InterviewState
│   │   │   └── workflow.py          # 工作流编排
│   │   └── utils/
│   │       └── api_client.py        # LLM API 封装
│   ├── data/
│   │   └── resume_loader.py         # Kaggle 2484 份简历数据集
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx             # 首页（选岗/上传简历）
│   │   │   ├── Interview.tsx        # 面试对话（SSE 流式）
│   │   │   └── Report.tsx           # 评估报告（雷达图/柱状图）
│   │   ├── api/
│   │   │   └── client.ts            # API 客户端
│   │   └── types/
│   │       └── index.ts             # TypeScript 类型定义
│   ├── nginx.conf                   # Nginx 生产配置
│   └── Dockerfile
├── docker-compose.yml               # 一键部署
├── .env.example
└── README.md
```

## 核心工作流

```
START → 简历分析 Agent → 面试官 Agent → 候选人回答
                                    ↓
                              评估 Agent（评分）
                                    ↓
                    得分 ≥ 70? ──是──→ 下一个主问题
                          ↓否
                       追问（最多3次）
                          ↓
                 5个主问题完成 → 最终报告 Agent
```

**5 个高价值考察方向：**
1. 技术深度：核心技能的底层原理、最佳实践
2. 项目经验：架构决策、权衡取舍
3. 问题解决：模糊需求/线上故障的分析思路
4. 系统设计：可扩展系统的全局设计能力
5. 协作与成长：团队协作、技术规划

## 技术栈

| 层 | 技术 |
|---|---|
| **前端** | React 18, TypeScript, Vite, Tailwind CSS 4, Recharts |
| **后端** | FastAPI, LangGraph, LangChain, Pydantic |
| **AI** | DeepSeek Chat API（OpenAI 兼容） |
| **数据库** | SQLite（开发）/ PostgreSQL 16 + pgvector（生产） |
| **缓存** | Redis 7 |
| **存储** | MinIO |
| **部署** | Docker Compose |
