# 零成本部署完整教程

> 全程不花一分钱，约 30 分钟上线你的 AI 面试产品。

---

## 前提准备（5 分钟）

### 你需要有：

| 东西 | 说明 | 怎么搞 |
|------|------|--------|
| **GitHub 账号** | 存放代码 | [github.com](https://github.com) 免费注册 |
| **DeepSeek API Key** | AI 大模型调用 | [platform.deepseek.com](https://platform.deepseek.com) 注册 → API Keys → 创建，**充值 ¥10 即可** |
| **Vercel 账号** | 部署前端 | [vercel.com](https://vercel.com) 点 "Sign Up" → 用 GitHub 登录 |
| **Railway 账号** | 部署后端 | [railway.app](https://railway.app) 点 "Start a New Project" → 用 GitHub 登录 |

### 你的 DeepSeek API Key 长这样：

```
sk-6090e962598b419ebc03b4ebc937769e
```

> 现在去 deepseek 平台注册充值 ¥10，**这 10 块够你用几千次面试**。

---

## 第一步：把代码推上 GitHub（5 分钟）

打开终端（项目根目录 `d:\Projects\ai_interview_v2`）：

```bash
# 1. 初始化 Git
git init

# 2. 创建 .gitignore（排除不需要上传的文件）
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
*.db
node_modules/
dist/
.vite/
EOF

# 3. 添加所有文件并提交
git add .
git commit -m "AI面试系统 v3.0 - 零成本商用版"

# 4. 在 GitHub 上创建新仓库（网页操作）
#    打开 github.com → 右上角 + 号 → New repository
#    仓库名填：ai-interview
#    选 Public（公开）
#    不要勾选任何初始化选项
#    点 Create repository

# 5. 关联远程仓库并推送（把下面网址换成你刚创建的仓库地址）
git remote add origin https://github.com/你的用户名/ai-interview.git
git branch -M main
git push -u origin main
```

> 推送成功后，刷新 GitHub 页面，你应该看到所有代码文件都在上面了。

---

## 第二步：部署后端到 Railway（10 分钟）

### 2.1 创建 Railway 项目

1. 打开 [railway.app](https://railway.app)，点右上角 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. Railway 会要求授权访问你的 GitHub，点 **"Authorize Railway"**
4. 在仓库列表里找到 `ai-interview`，点它
5. Railway 开始自动部署...然后会**失败**（正常，还没配环境变量）

### 2.2 配置环境变量

1. 在 Railway 项目页面，点顶部的 **"Variables"** 标签
2. 点 **"New Variable"**，逐个添加以下变量：

```
变量名                         值
────────────────────────────────────────────
DEEPSEEK_API_KEY              sk-你的DeepSeek密钥（换成你自己的）
DEEPSEEK_BASE_URL             https://api.deepseek.com/v1
MODEL_NAME                    deepseek-chat
DATABASE_URL                  sqlite:///./interview.db
JWT_SECRET                    随便打一串乱码比如 asdf1234xyz
```

3. 全部添加完后，页面看起来像一张表，6 行
4. 点右上角 **"Deploy"** 按钮，会重新部署
5. 这次应该成功了，看到绿色的 **"Active"** 或 **"Success"**

### 2.3 设置 Root Directory

Railway 需要知道你的后端代码在 `backend` 子目录里：

1. 在项目页面，点 **"Settings"** 标签
2. 找到 **"Root Directory"** 字段
3. 填入：`backend`
4. 点 **"Deploy"** 重新部署

### 2.4 获取后端域名

1. 部署成功后，点 **"Deployments"** 标签
2. 找到最新一次部署，应该有个域名链接，比如：
   ```
   https://ai-interview-production.up.railway.app
   ```
3. **把这个域名复制下来，存到记事本里**，下一步要用

### 2.5 验证后端是否正常

在浏览器打开：`https://你的域名.railway.app/api/health`

应该看到：
```json
{"status":"ok","version":"3.0.0","postgres":"sqlite","redis":"disabled"}
```

> 如果看到这个，后端部署成功！

---

## 第三步：部署前端到 Vercel（10 分钟）

### 3.1 先改一下配置文件

在你的项目里，有个文件 `frontend/vercel.json`，需要把后端域名改掉：

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://你的域名.railway.app/api/:path*" }
  ]
}
```

把 `你的域名.railway.app` 替换成你第二步获取的 Railway 域名。

改完后提交：

```bash
git add frontend/vercel.json
git commit -m "更新后端域名"
git push
```

### 3.2 创建 Vercel 项目

1. 打开 [vercel.com](https://vercel.com)，点右上角 **"New Project"**
2. 在列表里找到 `ai-interview`，点 **"Import"**
3. 在配置页面：
   - **Framework Preset**：选 `Vite`
   - **Root Directory**：点 "Edit"，填入 `frontend`
   - **Build Command**：保持默认 `npm run build`
   - **Output Directory**：保持默认 `dist`
4. 点 **"Deploy"**
5. 等待 1-2 分钟，构建完成

### 3.3 获取前端域名

1. 部署成功后，Vercel 会显示恭喜页面
2. 域名类似：`https://ai-interview-xxx.vercel.app`
3. **复制这个域名**，在浏览器打开

---

## 第四步：验证完整流程

### 4.1 打开你的网站

浏览器打开 Vercel 给你的域名（比如 `https://ai-interview-xxx.vercel.app`）

你应该看到：
- 登录/注册页面
- 输入用户名 `demo`、邮箱 `demo@test.com`、密码 `123456`
- 点击注册

### 4.2 开始面试

1. 登录后进入首页，顶部应该显示 **"免费试用 · 剩余 3 次"**
2. 选择「模拟简历」→ 选一个岗位类别 → 选一份简历
3. 输入目标岗位，比如「后端开发工程师」
4. 点击「开始面试」
5. 等待 AI 分析简历并生成第一个问题
6. 输入回答，回车发送
7. AI 实时评分，追问或进入下一题
8. 完成 5 个主问题后跳转到报告页

### 4.3 测试付费弹窗

1. 用完 3 次免费面试
2. 第 4 次点击「开始面试」→ 弹出支付弹窗
3. 弹窗显示月卡 ¥29 / 年卡 ¥199 + 付款说明

---

## 第五步：配置管理员 & 收款流程

### 5.1 创建管理员账号

在 Railway 项目页面，点 **"Command"** 标签（或点终端图标），输入：

```bash
python -c "
from app.models.db import init_db, get_session_factory
from app.models.db import User
init_db()
session = get_session_factory()()
import uuid
admin = User(
    id=str(uuid.uuid4()),
    username='admin',
    email='admin@admin.com',
    password_hash='',
    subscription_tier='admin',
    trial_interviews_used=0,
    max_trial_interviews=999
)
session.add(admin)
session.commit()
print('管理员已创建: admin')
"
```

### 5.2 收款流程

**你的收款流程：**

1. 用户用完 3 次试用，看到支付弹窗，联系你
2. 你发微信收款码（个人微信即可），用户扫码付 ¥29
3. 你在网页上登录 `admin` 账号
4. 调用升级 API（或者直接在 Railway 命令行执行）：

```bash
# 方式 1：用 Railway 命令行升级
python -c "
from app.models.db import get_session_factory, User
session = get_session_factory()()
user = session.query(User).filter(User.username == '要升级的用户名').first()
user.subscription_tier = 'pro'
user.max_trial_interviews = 999
session.commit()
print('已升级')
"

# 方式 2：用 curl 调用 API（需要先登录 admin 获取 token）
# curl -X POST https://你的域名/api/subscription/upgrade?username=用户名&tier=pro \
#   -H "Authorization: Bearer admin的JWT_Token"
```

5. 用户刷新页面，看到 "Pro 会员 · 无限使用"

---

## 第六步：自定义你的产品

### 改支付弹窗内容

编辑 `backend/app/api/subscription.py` 里的 `PAYMENT_INFO`：

```python
PAYMENT_INFO = {
    "price_monthly": 29,      # 改你的月卡价格
    "price_yearly": 199,      # 改你的年卡价格
    "qr_code_url": "",        # 上传收款码图片链接
    "contact": "付款后截图发给客服微信：你的微信号",  # 改你的联系方式
}
```

改完 `git push`，Railway 会自动重新部署。

### 改网站标题和文案

- 首页标题：`frontend/src/pages/Home.tsx` 搜索 "AI 模拟面试"
- 分享文案：`frontend/src/pages/Report.tsx` 搜索 "ai-interview.vercel.app"

---

## 常见问题

### Q: 面试时一直加载不出问题？

A: 检查 DeepSeek API Key 是否正确。在 Railway → Variables 里确认 `DEEPSEEK_API_KEY` 的值。也要确保 DeepSeek 平台账户里有余额。

### Q: 前端页面打不开？

A: Vercel 部署后需要等 1-2 分钟。如果 404，检查 Root Directory 是否设为 `frontend`。

### Q: 后端报 "Method Not Allowed"？

A: 检查 `vercel.json` 里的后端域名是否正确。注意结尾不要有多余的 `/`。

### Q: Railway 说 "部署失败"？

A: 最常见的原因是 Root Directory 没设。去 Settings → Root Directory 填 `backend`，然后点 Deploy。

### Q: 怎么绑定自己的域名？

A: Vercel 和 Railway 都支持自定义域名：
- Vercel：Settings → Domains → 添加你的域名，去域名服务商加 CNAME 记录
- Railway：Settings → Public Networking → Custom Domain

### Q: 数据存在哪里？会丢吗？

A: 当前存在 Railway 的临时磁盘（SQLite 文件）。免费方案下 Railway 重启可能丢数据。用户量起来后建议升级 Railway 的数据库服务（PostgreSQL，$5/月起），或等积累了付费用户再迁移。

---

## 成本总结

| 服务 | 月费 | 够支撑多少用户 |
|------|------|--------------|
| Vercel（前端） | ¥0 | 5 万 PV |
| Railway（后端） | ¥0（$5 免费额度） | ~500 次面试 |
| DeepSeek API | ¥0-50（按量） | ~0.3 元/次面试 |
| 微信收款 | ¥0（个人码） | 无限 |
| **合计** | **¥0-50/月** | **500-1000 用户** |
