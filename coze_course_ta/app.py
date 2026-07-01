from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .core import AssistantRequest, build_assistant_response


class CourseAssistantInput(BaseModel):
    mode: Literal["explain", "hint", "quiz", "plan", "mixed"] = Field(
        default="mixed",
        description="助教模式：讲解、提示、出题、计划，或自动判断。",
    )
    topic: str = Field(default="", description="知识点或学习主题，例如“二次函数”。")
    question: str = Field(default="", description="学生的具体问题或题目。")
    course: str = Field(default="通用课程", description="课程名称，例如数学、物理、英语。")
    grade: str = Field(default="中学", description="学生年级或水平。")
    difficulty: str = Field(default="适中", description="题目或讲解难度。")
    tone: str = Field(default="有趣", description="表达风格，例如有趣、严谨、鼓励。")
    days: int = Field(default=3, ge=1, le=14, description="学习计划天数。")
    quiz_count: int = Field(default=3, ge=1, le=8, description="生成练习题数量。")


app = FastAPI(
    title="Coze Course Teaching Assistant",
    description="给 Coze Bot 调用的趣味课程助教工具。",
    version="1.0.0",
    servers=[
        {
            "url": "https://coze-course-ta.onrender.com",
            "description": "Render production service",
        }
    ],
)
app.openapi_version = "3.0.3"


@app.get("/health", summary="服务健康检查")
def health() -> dict:
    return {"ok": True, "service": "coze_course_ta"}


@app.post(
    "/assistant",
    operation_id="course_assistant",
    summary="课程助教工具",
    description="根据模式生成知识点讲解、分层提示、练习题或学习计划。",
)
def assistant(payload: CourseAssistantInput) -> dict:
    request = AssistantRequest(**payload.model_dump())
    return build_assistant_response(request)
