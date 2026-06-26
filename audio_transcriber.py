from transformers import pipeline
import torch


# Use the smallest Whisper model for the fastest transcription.
# "whisper-small" is more accurate than "whisper-tiny", but "whisper-tiny" is much faster.
# If you want a balance between speed and quality, use "openai/whisper-small" or "openai/whisper-medium".
MODEL_NAME = "openai/whisper-tiny"

USE_GPU = torch.cuda.is_available()
DEVICE = 0 if USE_GPU else -1
PIPE_KWARGS = {}
if USE_GPU:
    PIPE_KWARGS["torch_dtype"] = torch.float16


pipe = pipeline(
    "automatic-speech-recognition",
    model=MODEL_NAME,
    device=DEVICE,
    chunk_length_s=30,
    **PIPE_KWARGS,
)

def transcribe_audio(audio_file):
    result = pipe(audio_file)
    return result["text"]

#if __name__ == "__main__":
    #transcribe_audio("practice.mp3")
