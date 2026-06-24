from pathlib import Path


def test_check_env_mentions_playwright_browser_check():
    text = Path("scripts/check-env.sh").read_text(encoding="utf-8")
    assert "playwright" in text
    assert "chromium" in text.lower()


def test_check_env_prefers_project_virtualenv_python():
    text = Path("scripts/check-env.sh").read_text(encoding="utf-8")
    assert ".venv/bin/python" in text
