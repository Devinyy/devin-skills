from unittest.mock import patch

from scripts.extract_audio import normalize_audio


def test_normalize_audio_invokes_ffmpeg_for_16k_mono_wav(tmp_path):
    source = tmp_path / "input.mp4"
    output = tmp_path / "audio.wav"
    source.write_bytes(b"placeholder")

    with patch("scripts.extract_audio.subprocess.run") as run:
        result = normalize_audio(source, output)

    assert result == output
    run.assert_called_once_with(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(output),
        ],
        check=True,
    )
