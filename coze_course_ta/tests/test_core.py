from coze_course_ta.core import AssistantRequest, build_assistant_response


def test_explain_response_has_expected_sections():
    response = build_assistant_response(
        AssistantRequest(mode="explain", topic="二次函数", course="数学")
    )

    assert response["mode"] == "explain"
    assert "二次函数" in response["title"]
    assert "one_sentence" in response["payload"]
    assert response["payload"]["steps"]


def test_mixed_mode_routes_to_plan():
    response = build_assistant_response(
        AssistantRequest(mode="mixed", topic="三天复习牛顿第二定律计划", course="物理")
    )

    assert response["mode"] == "plan"
    assert response["payload"]["days"] == 3


def test_quiz_count_is_limited():
    response = build_assistant_response(
        AssistantRequest(mode="quiz", topic="英语现在完成时", quiz_count=99)
    )

    assert response["mode"] == "quiz"
    assert response["payload"]["count"] == 8
    assert len(response["payload"]["questions"]) == 8
