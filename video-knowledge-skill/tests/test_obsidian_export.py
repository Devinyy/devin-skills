import json

from scripts.obsidian_export import classify_category, detect_vault, export_summary, normalize_category, parse_model_category, safe_filename


def test_detect_vault_uses_open_recent_vault(tmp_path, monkeypatch):
    older = tmp_path / "older"
    newer = tmp_path / "newer"
    older.mkdir()
    newer.mkdir()
    config = tmp_path / "obsidian.json"
    config.write_text(
        json.dumps(
            {
                "vaults": {
                    "a": {"path": str(older), "ts": 10, "open": False},
                    "b": {"path": str(newer), "ts": 20, "open": True},
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)

    assert detect_vault(config) == newer


def test_detect_vault_env_override(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(vault))

    assert detect_vault(tmp_path / "missing.json") == vault


def test_export_summary_copies_to_vault_category(tmp_path):
    task = tmp_path / "outputs" / "task123"
    task.mkdir(parents=True)
    (task / "summary.md").write_text("# 标题：AI/Coding?\n\n代码质量和软件工程内容", encoding="utf-8")
    vault = tmp_path / "vault"
    vault.mkdir()

    exported = export_summary(task, vault=vault)

    assert exported == vault / "研发" / "工程质量" / "标题：AI Coding.md"
    exported_text = exported.read_text(encoding="utf-8")
    assert exported_text.startswith("# 标题：AI/Coding?\n\n代码质量和软件工程内容")
    assert "## Obsidian 关联" in exported_text
    assert "[[_索引/研发|研发]]" in exported_text
    assert "[[_索引/研发/工程质量|工程质量]]" in exported_text
    assert (vault / "_索引" / "研发.md").exists()
    assert (vault / "_索引" / "研发" / "工程质量.md").exists()
    metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["obsidian_category"] == "研发/工程质量"
    assert metadata["obsidian_category_method"] == "rules"


def test_export_summary_honors_optional_subdir(tmp_path):
    task = tmp_path / "outputs" / "task123"
    task.mkdir(parents=True)
    (task / "summary.md").write_text("# 旅行攻略\n\n酒店和路线", encoding="utf-8")
    vault = tmp_path / "vault"
    vault.mkdir()

    exported = export_summary(task, vault=vault, subdir="Inbox")

    assert exported == vault / "Inbox" / "生活" / "旅行" / "旅行攻略.md"


def test_classify_category_prefers_agent_for_agent_content(tmp_path):
    task = tmp_path / "outputs" / "task123"
    task.mkdir(parents=True)
    summary = task / "summary.md"
    summary.write_text("# Coding Agent 实践\n\nAgent 自动规划和工具调用", encoding="utf-8")

    category, method, reason = classify_category(task, summary)

    assert category == "AI工程/Agent"
    assert method == "rules"
    assert reason


def test_classify_category_can_be_overridden(tmp_path, monkeypatch):
    task = tmp_path / "outputs" / "task123"
    task.mkdir(parents=True)
    summary = task / "summary.md"
    summary.write_text("# Coding Agent 实践\n\nAgent 自动规划和工具调用", encoding="utf-8")
    monkeypatch.setenv("OBSIDIAN_CATEGORY", "harness")

    category, method, reason = classify_category(task, summary)

    assert category == "AI工程/Harness"
    assert method == "env"
    assert "手动指定" in reason


def test_parse_model_category_json():
    parsed = parse_model_category('{"category":"AI工程/Harness","reason":"重点讨论评测基建"}')

    assert parsed == ("AI工程/Harness", "重点讨论评测基建")


def test_normalize_legacy_category():
    assert normalize_category("Agent") == "AI工程/Agent"
    assert normalize_category("研发") == "研发/架构"


def test_safe_filename_has_fallback():
    assert safe_filename(" /:*? ", fallback="task123") == "task123"
