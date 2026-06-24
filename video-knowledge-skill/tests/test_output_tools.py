import json
import runpy
import sys


def test_list_outputs_reports_metadata_rows(tmp_path, monkeypatch, capsys):
    task = tmp_path / "abc123"
    task.mkdir()
    (task / "metadata.json").write_text(
        json.dumps({"platform": "douyin", "title": "标题", "metadata": {"content_type": "video"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["list-outputs.py", str(tmp_path)])

    runpy.run_path("scripts/list-outputs.py", run_name="__main__")

    out = capsys.readouterr().out
    assert "abc123" in out
    assert "douyin" in out
    assert "标题" in out


def test_clean_empty_outputs_removes_empty_directories(tmp_path, monkeypatch):
    empty = tmp_path / "empty"
    empty.mkdir()
    full = tmp_path / "full"
    full.mkdir()
    (full / "metadata.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["clean-empty-outputs.py", str(tmp_path)])

    runpy.run_path("scripts/clean-empty-outputs.py", run_name="__main__")

    assert not empty.exists()
    assert full.exists()
