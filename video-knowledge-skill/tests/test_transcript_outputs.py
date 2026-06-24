from scripts.transcribe import format_srt_timestamp, render_srt


def test_format_srt_timestamp():
    assert format_srt_timestamp(65.432) == "00:01:05,432"


def test_render_srt_segments():
    segments = [{"start": 0.0, "end": 1.5, "text": "你好"}]
    assert render_srt(segments) == "1\n00:00:00,000 --> 00:00:01,500\n你好\n"
