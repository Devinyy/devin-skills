import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def run_batch(monkeypatch, argv, returncodes):
    calls = []
    codes = list(returncodes)

    def fake_run(cmd, check=False):
        calls.append(cmd)
        return SimpleNamespace(returncode=codes.pop(0))

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(sys, "argv", argv)
    try:
        runpy.run_path("scripts/batch-extract.py", run_name="__main__")
    except SystemExit as exc:
        return calls, int(exc.code or 0)
    return calls, 0


def test_batch_extract_passes_transcription_options_to_each_item(tmp_path, monkeypatch):
    inputs = tmp_path / "inputs.txt"
    inputs.write_text("https://example.test/one\nhttps://example.test/two\n", encoding="utf-8")
    output = tmp_path / "outputs"

    calls, code = run_batch(
        monkeypatch,
        [
            "batch-extract.py",
            str(inputs),
            "--output",
            str(output),
            "--transcribe",
            "--summarize",
            "--transcribe-backend",
            "mlx",
            "--model-size",
            "small",
            "--language",
            "zh",
            "--summary-style",
            "note",
        ],
        [0, 0],
    )

    assert code == 0
    assert len(calls) == 2
    for cmd in calls:
        assert "--transcribe-backend" in cmd
        assert "mlx" in cmd
        assert "--model-size" in cmd
        assert "small" in cmd
        assert "--language" in cmd
        assert "zh" in cmd
        assert "--summary-style" in cmd
        assert "note" in cmd


def test_batch_extract_records_queue_status_and_continues_after_failure(tmp_path, monkeypatch):
    inputs = tmp_path / "inputs.txt"
    inputs.write_text("https://example.test/ok\nhttps://example.test/fail\n", encoding="utf-8")
    output = tmp_path / "outputs"

    calls, code = run_batch(
        monkeypatch,
        ["batch-extract.py", str(inputs), "--output", str(output)],
        [0, 3],
    )

    queue = json.loads((output / "batch-queue.json").read_text(encoding="utf-8"))
    assert code == 1
    assert len(calls) == 2
    assert [item["status"] for item in queue["items"]] == ["done", "failed"]
    assert [item["returncode"] for item in queue["items"]] == [0, 3]


def test_batch_extract_resume_skips_done_items(tmp_path, monkeypatch):
    inputs = tmp_path / "inputs.txt"
    inputs.write_text("https://example.test/one\nhttps://example.test/two\n", encoding="utf-8")
    output = tmp_path / "outputs"
    output.mkdir()
    queue = {
        "input_file": str(inputs),
        "items": [
            {"source": "https://example.test/one", "status": "done", "attempts": 1, "returncode": 0},
            {"source": "https://example.test/two", "status": "pending", "attempts": 0, "returncode": None},
        ],
    }
    (output / "batch-queue.json").write_text(json.dumps(queue), encoding="utf-8")

    calls, code = run_batch(
        monkeypatch,
        ["batch-extract.py", str(inputs), "--output", str(output), "--resume"],
        [0],
    )

    assert code == 0
    assert len(calls) == 1
    assert "https://example.test/two" in calls[0]
