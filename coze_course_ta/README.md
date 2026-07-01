# Coze 趣味课程助教 Bot

这是一个给 Coze Bot 配套使用的 Python 助教服务。推荐架构是：

1. Coze 负责聊天、记忆、工作流和大模型表达。
2. 这个 Python 服务负责稳定、可复用的课程助教工具，例如讲解、提示、出题、学习计划。
3. Coze 通过“插件/工具/OpenAPI 导入”的方式调用这个服务。

这样做的好处是：Bot 的说话风格可以在 Coze 里快速调整，而真正的课程功能写在 Python 里，后面你想加“错题本”“课程表”“积分系统”都会更清楚。

## 这个 Bot 能做什么

- `explain`：把一个知识点讲成“一句话、类比、步骤、易错点、小挑战”。
- `hint`：对题目给分层提示，不直接把答案塞给学生。
- `quiz`：按主题生成选择题、答案和解析。
- `plan`：生成若干天的学习计划。
- `mixed`：让服务根据输入自动选择模式。

## 本地运行

进入项目根目录后执行：

```powershell
cd E:\huaxin-extension\coze_course_ta
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

打开：

- 本地接口文档：`http://127.0.0.1:8000/docs`
- OpenAPI 地址：`http://127.0.0.1:8000/openapi.json`
- 健康检查：`http://127.0.0.1:8000/health`

## 先本地测试一次

```powershell
curl -X POST http://127.0.0.1:8000/assistant `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"explain\",\"topic\":\"牛顿第二定律\",\"course\":\"物理\",\"grade\":\"初中\",\"tone\":\"有趣\"}"
```

如果 Windows PowerShell 显示中文乱码，通常只是终端编码问题。可以用浏览器打开 `http://127.0.0.1:8000/docs` 测试，或者用 Python/Coze 发 UTF-8 JSON，请求本身支持中文。

## 接到 Coze 网页

Coze 这类 Bot 平台通常不能直接访问你电脑上的 `127.0.0.1`，所以你需要把 Python 服务部署到一个公网地址。常见选择：

- 学习测试：Render、Railway、Fly.io、Vercel Serverless、云服务器。
- 临时演示：ngrok 或 cloudflared，把本地 `8000` 映射成一个公网 HTTPS 地址。
- 正式使用：腾讯云、阿里云、火山引擎等云服务器。

拿到公网地址后，例如：

```text
https://your-domain.example.com/openapi.json
```

在 Coze 网页里大致这样配置：

1. 新建 Bot，名称可以叫“妙趣课程助教”。
2. 把 `coze_bot_prompt.md` 里的提示词复制到 Bot 的角色设定/Prompt。
3. 找到工具、插件、自定义插件或 OpenAPI 导入入口。
4. 选择从 URL 导入 OpenAPI。
5. 填入你的公网 OpenAPI 地址：`https://你的域名/openapi.json`。
6. 导入后，确认出现 `course_assistant` 或 `/assistant` 工具。
7. 在 Bot 对话里测试：“用有趣的方式讲一下二次函数，并给我 3 道题。”

如果你的 Coze 界面按钮名字和这里略有不同，核心思路不变：导入这个 Python 服务生成的 OpenAPI，然后让 Bot 在需要讲解、出题、规划时调用它。

## 用 Render 部署

这个仓库根目录已经提供了 `render.yaml`。Render 读取它以后会自动知道：

- 服务目录是 `coze_course_ta`
- 构建命令是 `pip install -r requirements.txt`
- 启动命令是 `uvicorn app:app --host 0.0.0.0 --port $PORT`
- 健康检查地址是 `/health`

部署步骤：

1. 把当前代码推送到 GitHub 仓库。
2. 打开 Render Dashboard，选择新建 Blueprint 或 Web Service。
3. 连接你的 GitHub 仓库。
4. 如果选择 Blueprint，Render 会读取根目录的 `render.yaml`。
5. 如果选择 Web Service，则手动填写：
   - Root Directory: `coze_course_ta`
   - Language: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. 部署成功后，Render 会给你一个 `https://xxx.onrender.com` 地址。
7. 测试：
   - `https://xxx.onrender.com/health`
   - `https://xxx.onrender.com/openapi.json`
8. 在 Coze 导入：
   - `https://xxx.onrender.com/openapi.json`

## 设计原理

### 1. 为什么不用 Python 直接替代 Coze

Coze 的优势是对话编排、模型能力、知识库、工作流和发布渠道。Python 的优势是写清楚的业务逻辑。把二者拆开以后：

- 想改 Bot 人设，在 Coze 改 Prompt。
- 想改功能规则，在 Python 改函数。
- 想接数据库、课程表、错题本，在 Python 扩展。

### 2. 为什么用 FastAPI

FastAPI 会自动生成 OpenAPI 文档。Coze 导入工具时通常需要理解接口输入和输出，OpenAPI 就相当于“接口说明书”。我们只要写好 Python 类型，FastAPI 会帮你生成 `/openapi.json`。

### 3. 为什么提示模式不直接给答案

真正的课程助教不应该只做答案机器。`hint` 模式会给“观察方向、关键公式、下一步尝试”，让学生先动脑；如果用户明确要完整解析，Coze 再根据场景组织答案。

### 4. 以后怎么升级

可以继续加：

- 错题本：接 SQLite/PostgreSQL，保存学生常错点。
- 课程知识库：Coze 知识库或 Python 检索教材资料。
- 积分系统：每完成一次小挑战加分。
- 教师模式：生成教案、板书、课堂互动题。
- 班级模式：按学生水平自动分层练习。
