import json

from scripts.obsidian_export import classify_category, detect_vault, export_summary, safe_filename


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

    assert exported == vault / "研发" / "标题：AI Coding.md"
    assert exported.read_text(encoding="utf-8") == "# 标题：AI/Coding?\n\n代码质量和软件工程内容"


def test_export_summary_honors_optional_subdir(tmp_path):
    task = tmp_path / "outputs" / "task123"
    task.mkdir(parents=True)
    (task / "summary.md").write_text("# 旅行攻略\n\n酒店和路线", encoding="utf-8")
    vault = tmp_path / "vault"
    vault.mkdir()

    exported = export_summary(task, vault=vault, subdir="Inbox")

    assert exported == vault / "Inbox" / "旅行" / "旅行攻略.md"


def test_classify_category_prefers_agent_for_agent_content(tmp_path):
    task = tmp_path / "outputs" / "task123"
    task.mkdir(parents=True)
    summary = task / "summary.md"
    summary.write_text("# Coding Agent 实践\n\nAgent 自动规划和工具调用", encoding="utf-8")

    assert classify_category(task, summary) == "Agent"


def test_safe_filename_has_fallback():
    assert safe_filename(" /:*? ", fallback="task123") == "task123"
