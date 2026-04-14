import sys
import time
import warnings
import logging
import contextlib
import io

# Suppress noisy warnings from transformers/torch
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

print("Loading imports...")
t0 = time.time()

import torch
import librosa
from transformers import WhisperForConditionalGeneration, WhisperProcessor

print(f"Imports loaded in {time.time() - t0:.1f}s")

from config import WHISPER_MODEL_ID


def transcribe(audio_path: str) -> str:
    total_start = time.time()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    print("Loading model...")
    t = time.time()
    processor = WhisperProcessor.from_pretrained(WHISPER_MODEL_ID)
    model = WhisperForConditionalGeneration.from_pretrained(WHISPER_MODEL_ID).to(device)
    model.eval()
    print(f"Model loaded in {time.time() - t:.1f}s")

    print(f"Loading audio: {audio_path}")
    t = time.time()
    audio, sr = librosa.load(audio_path, sr=16000)
    duration = len(audio) / sr
    print(f"Audio loaded in {time.time() - t:.1f}s ({duration:.1f}s of audio)")

    chunk_size = 30 * sr
    chunks = [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]
    print(f"Split into {len(chunks)} chunks of ~30s each")

    forced_decoder_ids = processor.get_decoder_prompt_ids(language="hebrew", task="transcribe")
    full_text = []

    for i, chunk in enumerate(chunks):
        t = time.time()
        inputs = processor(chunk, sampling_rate=16000, return_tensors="pt")
        input_features = inputs.input_features.to(device)

        with torch.no_grad(), contextlib.redirect_stderr(io.StringIO()):
            predicted_ids = model.generate(
                input_features,
                forced_decoder_ids=forced_decoder_ids,
            )

        text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        elapsed = time.time() - t
        print(f"  Chunk {i+1}/{len(chunks)} done in {elapsed:.1f}s: {text[:60]}...")
        full_text.append(text)

    print(f"\nTotal transcription time: {time.time() - total_start:.1f}s")
    return " ".join(full_text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file>")
        sys.exit(1)

    text = transcribe(sys.argv[1])
    print("\n--- Transcription ---")
    print(text)
