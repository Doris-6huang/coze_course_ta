# coze_course_ta

Coze 趣味课程助教 Bot 的 Python API 服务。

主要文件：

- `coze_course_ta/app.py`：FastAPI 接口入口
- `coze_course_ta/core.py`：课程助教核心逻辑
- `coze_course_ta/coze_bot_prompt.md`：复制到 Coze 的 Bot 提示词
- `requirements.txt`：Render 从仓库根目录构建时使用的依赖文件
- `render.yaml`：Render 一键部署配置

Render 部署后，把下面地址导入 Coze 的 OpenAPI 工具：

```text
https://你的-render-地址/openapi.json
```

本地运行和 Coze 配置说明见 `coze_course_ta/README.md`。
