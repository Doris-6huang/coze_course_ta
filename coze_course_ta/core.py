from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal


Mode = Literal["explain", "hint", "quiz", "plan", "mixed"]


@dataclass(frozen=True)
class AssistantRequest:
    mode: Mode = "mixed"
    topic: str = ""
    question: str = ""
    course: str = "通用课程"
    grade: str = "中学"
    difficulty: str = "适中"
    tone: str = "有趣"
    days: int = 3
    quiz_count: int = 3


def build_assistant_response(request: AssistantRequest) -> dict:
    mode = _resolve_mode(request)
    if mode == "explain":
        payload = explain_topic(request)
    elif mode == "hint":
        payload = build_hint_ladder(request)
    elif mode == "quiz":
        payload = build_quiz(request)
    elif mode == "plan":
        payload = build_study_plan(request)
    else:
        payload = explain_topic(request)

    return {
        "mode": mode,
        "title": _title_for(request, mode),
        "course": request.course,
        "grade": request.grade,
        "difficulty": request.difficulty,
        "payload": payload,
        "next_actions": _next_actions(mode),
    }


def explain_topic(request: AssistantRequest) -> dict:
    topic = _main_subject(request)
    metaphor = _metaphor(topic, request.course)
    return {
        "one_sentence": f"{topic} 的核心是：先抓住主要关系，再用规则一步步推出来。",
        "metaphor": metaphor,
        "steps": [
            f"先问自己：{topic} 里有哪些对象？",
            "再找对象之间的关系，例如因果、数量、变化或结构。",
            "把关系写成一句话、图示、公式或表格。",
            "最后用一个小例子验证自己有没有真的理解。",
        ],
        "common_mistakes": [
            "只背结论，不知道结论从哪里来。",
            "看到题目就套公式，没有先判断条件是否匹配。",
            "会做熟题，但换个说法就不知道它还是同一个知识点。",
        ],
        "mini_challenge": f"请你用自己的话解释一次“{topic}”，并举一个生活里的例子。",
    }


def build_hint_ladder(request: AssistantRequest) -> dict:
    subject = _main_subject(request)
    question = request.question.strip() or f"关于 {subject} 的题目"
    return {
        "question_seen": question,
        "hint_1": f"先别急着算。圈出题目中和“{subject}”最相关的关键词。",
        "hint_2": "把已知条件和要求的结果分开写，看看中间缺哪一步。",
        "hint_3": "尝试找一个最小例子，或者把复杂条件改成简单数字先试一遍。",
        "check_yourself": "如果你的每一步都能说出“为什么”，这道题基本就稳了。",
        "teacher_note": "如果学生继续卡住，再给公式、图示或完整解析。",
    }


def build_quiz(request: AssistantRequest) -> dict:
    topic = _main_subject(request)
    count = min(max(request.quiz_count, 1), 8)
    templates = [
        {
            "question": f"学习“{topic}”时，第一步最应该做什么？",
            "options": {
                "A": "立刻背最后结论",
                "B": "先找对象、条件和关系",
                "C": "只做最难的题",
                "D": "跳过例题直接考试",
            },
            "answer": "B",
            "explanation": "理解一个知识点，先找到对象、条件和关系，后面的公式或方法才有位置。",
        },
        {
            "question": f"下面哪种情况最可能说明你还没有真正理解“{topic}”？",
            "options": {
                "A": "能举一个自己的例子",
                "B": "能说出常见易错点",
                "C": "题目换个说法就完全认不出来",
                "D": "能把步骤讲给同学听",
            },
            "answer": "C",
            "explanation": "真正理解后，即使题目换了包装，也能看出背后的同一个知识点。",
        },
        {
            "question": f"如果你想把“{topic}”讲给朋友听，最好的方式是？",
            "options": {
                "A": "只念一遍定义",
                "B": "只说答案，不说过程",
                "C": "先用生活例子引入，再讲规则",
                "D": "告诉他不会就算了",
            },
            "answer": "C",
            "explanation": "生活例子能降低理解门槛，规则能保证表达准确。",
        },
        {
            "question": f"复习“{topic}”时，最值得放进错题本的是？",
            "options": {
                "A": "只抄正确答案",
                "B": "记录错因、关键条件和下次提醒",
                "C": "把所有题目都抄一遍",
                "D": "只写一句“我粗心了”",
            },
            "answer": "B",
            "explanation": "错题本最重要的是帮助你下次避开同类错误，而不是收藏题目。",
        },
    ]
    questions = []
    for index in range(1, count + 1):
        template = templates[_stable_number(f"{topic}-{index}", len(templates))]
        questions.append(
            {
                "id": index,
                "type": "single_choice",
                **template,
            }
        )
    return {
        "topic": topic,
        "count": count,
        "questions": questions,
        "after_quiz": "做完后请让学生说出错题原因，而不是只记录正确选项。",
    }


def build_study_plan(request: AssistantRequest) -> dict:
    topic = _main_subject(request)
    days = min(max(request.days, 1), 14)
    plan = []
    for day in range(1, days + 1):
        plan.append(
            {
                "day": day,
                "focus": _plan_focus(day, topic),
                "tasks": [
                    f"用 10 分钟复述 {topic} 的核心概念。",
                    "做 2 道基础题，确认概念没有漏。",
                    "做 1 道变式题，观察题目换了什么说法。",
                ],
                "fun_check": "用一句像讲给朋友听的话总结今天学到的东西。",
            }
        )
    return {
        "topic": topic,
        "days": days,
        "plan": plan,
        "review_rule": "第 1 天学会，第 2 天复述，第 4 天回看错题，第 7 天做一次混合练习。",
    }


def _resolve_mode(request: AssistantRequest) -> Mode:
    if request.mode != "mixed":
        return request.mode

    text = f"{request.topic} {request.question}".lower()
    if any(word in text for word in ["计划", "安排", "复习", "schedule", "plan"]):
        return "plan"
    if any(word in text for word in ["题", "quiz", "练习", "测试", "选择题"]):
        return "quiz"
    if any(word in text for word in ["提示", "思路", "hint", "不会", "卡住"]):
        return "hint"
    return "explain"


def _main_subject(request: AssistantRequest) -> str:
    return request.topic.strip() or request.question.strip() or "这个知识点"


def _title_for(request: AssistantRequest, mode: Mode) -> str:
    topic = _main_subject(request)
    labels = {
        "explain": "知识点拆解",
        "hint": "分层提示",
        "quiz": "趣味练习",
        "plan": "学习计划",
        "mixed": "课程助教",
    }
    return f"{labels[mode]}：{topic}"


def _metaphor(topic: str, course: str) -> str:
    if "数学" in course or any(key in topic for key in ["函数", "方程", "几何", "概率"]):
        return f"可以把 {topic} 想成一张地图：条件是路标，结论是目的地，公式是路线。"
    if "物理" in course or any(key in topic for key in ["力", "速度", "电", "能量"]):
        return f"可以把 {topic} 想成一台机器：输入条件，观察变化，再解释为什么这样动。"
    if "语文" in course or any(key in topic for key in ["作文", "阅读", "修辞"]):
        return f"可以把 {topic} 想成侦探破案：线索在文本里，答案要有证据。"
    if "英语" in course or any(key in topic.lower() for key in ["grammar", "word", "english"]):
        return f"可以把 {topic} 想成搭积木：词汇是积木，语法决定怎么拼。"
    return f"可以把 {topic} 想成闯关游戏：先看规则，再过小关，最后挑战综合题。"


def _plan_focus(day: int, topic: str) -> str:
    focuses = [
        f"认识 {topic} 的基本规则",
        f"用例题理解 {topic}",
        f"整理 {topic} 的易错点",
        f"做 {topic} 的变式训练",
    ]
    return focuses[(day - 1) % len(focuses)]


def _next_actions(mode: Mode) -> list[str]:
    actions = {
        "explain": ["让学生复述", "生成 3 道练习", "换一个生活类比"],
        "hint": ["等待学生尝试", "给下一层提示", "需要时再完整解析"],
        "quiz": ["批改答案", "整理错因", "按错题再讲一次"],
        "plan": ["确认每天可用时间", "加入错题复盘", "设置阶段测验"],
        "mixed": ["继续追问目标", "选择讲解或练习"],
    }
    return actions[mode]


def _stable_number(text: str, modulo: int) -> int:
    digest = sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo
