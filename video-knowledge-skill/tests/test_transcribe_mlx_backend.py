from unittest.mock import Mock, patch

from scripts.transcribe import mlx_model_name, transcribe


def test_mlx_model_name_maps_common_sizes():
    assert mlx_model_name("tiny") == "mlx-community/whisper-tiny"
    assert mlx_model_name("base") == "mlx-community/whisper-base-mlx"
    assert mlx_model_name("small") == "mlx-community/whisper-small-mlx"
    assert mlx_model_name("mlx-community/whisper-large-v3-turbo") == "mlx-community/whisper-large-v3-turbo"


def test_transcribe_uses_mlx_backend(tmp_path):
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"placeholder")

    with patch("scripts.transcribe.mlx_whisper") as mlx:
        mlx.transcribe.return_value = {
            "language": "zh",
            "text": "你好",
            "segments": [
                {"start": 0.0, "end": 1.0, "text": "你好"},
            ],
        }
        payload = transcribe(str(audio), str(tmp_path), model_size="tiny", language="zh", backend="mlx")

    mlx.transcribe.assert_called_once_with(
        str(audio),
        path_or_hf_repo="mlx-community/whisper-tiny",
        language="zh",
        verbose=False,
    )
    assert payload["backend"] == "mlx"
    assert payload["segments"][0]["text"] == "你好"
    assert (tmp_path / "transcript.srt").exists()
