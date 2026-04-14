# ivrit - Hebrew Meeting Transcriber & Summarizer

Transcribe Hebrew audio files and generate structured meeting summaries using AI.

Uses [ivrit-ai/whisper-large-v3](https://huggingface.co/ivrit-ai/whisper-large-v3) — a Whisper model fine-tuned on 5,000+ hours of Hebrew audio by [ivrit.ai](https://www.ivrit.ai), a non-profit making Hebrew a first-class citizen for AI.

## Features

- Hebrew speech-to-text using Whisper (optimized for Apple Silicon via MPS)
- Automatic meeting summarization with speaker identification, action items, key decisions, and more
- Caches transcripts so re-runs skip straight to summarization
- Supports multiple LLM providers: Gemini (default), Claude, Ollama
- RTL markdown output

## Project Structure

```
ivrit/
├── main.py           # Full pipeline: transcribe -> summarize -> save
├── transcribe.py     # Speech-to-text using ivrit-ai Whisper model
├── summarize.py      # LLM summarization (Gemini / Claude / Ollama)
├── config.py         # All settings: model IDs, LLM provider, API keys
├── requirements.txt  # Python dependencies
└── .env              # API keys (not committed)
```

### How it works

1. **`transcribe.py`** loads the audio, splits it into 30-second chunks (Whisper's native window), and runs inference on each chunk using MPS (Apple Silicon GPU) or CPU.

2. **`summarize.py`** sends the transcript to an LLM and gets back a structured summary with: speakers identified, general summary, action items, key decisions, important topics, and open questions.

3. **`main.py`** ties them together. It saves the transcript to `<filename>_transcript.txt` — if that file already exists on the next run, it skips transcription and goes straight to summarization.

4. **`config.py`** loads API keys from `.env` and holds all settings (model ID, LLM provider, Ollama model name).

## Setup

### Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (for m4a/mp3 audio support)
- [libsndfile](https://github.com/libsndfile/libsndfile) (audio processing)

```bash
# macOS
brew install ffmpeg libsndfile
```

### Install

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ivrit.git
cd ivrit

# Create a conda environment (recommended)
conda create -n ivrit python=3.12 -y
conda activate ivrit

# Install dependencies
pip install -r requirements.txt
```

### Configure

Create a `.env` file with your API key:

```
GEMINI_API_KEY=your-gemini-api-key
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

To use a different LLM provider, edit `config.py`:

```python
LLM_PROVIDER = "gemini"   # options: "gemini" | "claude" | "ollama"
```

## Usage

### Full pipeline (transcribe + summarize)

```bash
python main.py meeting.m4a
```

Output:
- `meeting_transcript.txt` — raw Hebrew transcript
- `meeting_summary.md` — structured RTL summary

Re-running the same file skips transcription (uses cached transcript).

### Transcribe only

```bash
python transcribe.py meeting.m4a
```

### Summarize an existing transcript

```bash
python summarize.py meeting_transcript.txt
```

## Performance

Tested on MacBook Pro M1 Pro with a 7-minute audio file:

| Step | Time |
|------|------|
| Import libraries | ~4s |
| Load model (cached) | ~7s |
| Load audio | ~1s |
| Transcription (15 chunks) | ~150s |
| Summarization (Gemini) | ~30s |
| **Total** | **~3 min** |

First run downloads the model (~6GB). Subsequent runs use the cached version at `~/.cache/huggingface/`.

To free up disk space later:

```bash
rm -rf ~/.cache/huggingface/hub/models--ivrit-ai--whisper-large-v3
```

## Supported Audio Formats

Any format supported by ffmpeg: `.m4a`, `.mp3`, `.wav`, `.ogg`, `.flac`, etc.

## LLM Providers

| Provider | Setup | Cost |
|----------|-------|------|
| **Gemini** (default) | API key from [aistudio.google.com](https://aistudio.google.com/apikey) | Free tier (20 req/day for Flash, 500/day for Flash Lite) |
| **Claude** | API key from [console.anthropic.com](https://console.anthropic.com) | Paid |
| **Ollama** | `brew install ollama` + `ollama pull llama3` | Free (local) |

## Credits

- [ivrit.ai](https://www.ivrit.ai) for the Hebrew Whisper model and datasets
- [Hugging Face](https://huggingface.co/ivrit-ai/whisper-large-v3) for model hosting
