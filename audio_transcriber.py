import torch

# "whisper-small" is more accurate than "whisper-tiny", but "whisper-tiny" is much faster.
MODEL_NAME = "openai/whisper-tiny"

_transcription_pipeline = None


def get_transcription_pipeline():
    global _transcription_pipeline

    if _transcription_pipeline is None:
        from transformers import pipeline

        use_gpu = torch.cuda.is_available()
        device = 0 if use_gpu else -1
        pipe_kwargs = {}
        if use_gpu:
            pipe_kwargs["torch_dtype"] = torch.float16

        _transcription_pipeline = pipeline(
            "automatic-speech-recognition",
            model=MODEL_NAME,
            device=device,
            chunk_length_s=30,
            **pipe_kwargs,
        )

    return _transcription_pipeline


def transcribe_audio(audio_file):
    try:
        pipe = get_transcription_pipeline()
        result = pipe(audio_file)
        return result["text"]
    except Exception:
        return ""
