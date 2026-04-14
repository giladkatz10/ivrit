import sys
import os

from transcribe import transcribe
from summarize import summarize


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    base = os.path.splitext(audio_file)[0]
    transcript_file = f"{base}_transcript.txt"
    summary_file = f"{base}_summary.md"

    # Step 1: Transcribe (skip if transcript already exists)
    print("\n" + "=" * 50)
    print("STEP 1: TRANSCRIPTION")
    print("=" * 50)

    if os.path.exists(transcript_file):
        print(f"Found existing transcript: {transcript_file}, skipping transcription.")
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = f.read()
    else:
        transcript = transcribe(audio_file)
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Saved transcript: {transcript_file}")

    print("\n--- Raw Transcript ---")
    print(transcript)

    # Step 2: Summarize
    print("\n" + "=" * 50)
    print("STEP 2: SUMMARIZATION")
    print("=" * 50)
    summary = summarize(transcript)

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print("\n--- Meeting Summary ---")
    print(summary)
    print(f"\nSaved summary: {summary_file}")
