from scripts.summarize import PROMPT, get_prompt


def test_dual_summary_prompt_contains_required_handoff_headings():
    for heading in [
        "## A. 忠实摘要",
        "## 一句话总结",
        "## 核心观点",
        "## 时间线",
        "## 关键知识点",
        "## 我的思考",
        "## B. 可收藏笔记",
        "## 笔记标题",
        "## 核心矛盾",
        "## 方法框架",
        "## 执行清单",
        "## 适用边界",
        "## 标签",
    ]:
        assert heading in PROMPT


def test_summary_prompt_requires_note_layer_to_avoid_fabrication():
    assert "允许适度重组、提炼标题和抽象框架" in PROMPT
    assert "不得新增原内容没有依据的事实" in PROMPT


def test_get_prompt_supports_summary_styles():
    assert "## A. 忠实摘要" in get_prompt("dual")
    assert "## B. 可收藏笔记" in get_prompt("dual")
    assert "## A. 忠实摘要" in get_prompt("faithful")
    assert "## B. 可收藏笔记" not in get_prompt("faithful")
    assert "## B. 可收藏笔记" in get_prompt("note")
    assert "## A. 忠实摘要" not in get_prompt("note")
