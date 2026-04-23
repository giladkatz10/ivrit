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

# (Optional) Login to HuggingFace to silence download warnings
huggingface-cli login
# Get a free token at https://huggingface.co/settings/tokens (Read access is enough)
```

### Configure

Create a `.env` file with your API key (see `.env.example`):

```
GEMINI_API_KEY=your-gemini-api-key
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

To use a different LLM provider, edit `config.py`:

```python
LLM_PROVIDER = "gemini"   # options: "gemini" | "claude" | "ollama"
```

## Quick Setup

### Option 1: Shell alias (terminal)

Add this to your `~/.zshrc` (update the path to where you cloned the repo):

```bash
echo 'alias ivrit="conda activate ivrit && python /path/to/ivrit/main.py"' >> ~/.zshrc
source ~/.zshrc
```

Now you can run from anywhere:

```bash
ivrit meeting.m4a
```

### Option 2: macOS right-click Quick Action

1. Open **Automator** (Spotlight → "Automator")
2. Create a new **Quick Action**
3. Set **"Workflow receives"** to **files or folders** in **Finder**
4. Drag **"Run Shell Script"** from the sidebar
5. Set **"Pass input"** to **as arguments**
6. Paste this (update paths if needed):
   ```bash
   WAS_RUNNING=$(osascript -e 'application "iTerm" is running')

   osascript <<EOF
   tell application "iTerm"
       activate
       if "$WAS_RUNNING" is "false" then
           tell current session of current window
               write text "conda activate ivrit && python '/path/to/ivrit/main.py' '$1'"
           end tell
       else
           tell current window to create tab with default profile
           tell current session of current window
               write text "conda activate ivrit && python '/path/to/ivrit/main.py' '$1'"
           end tell
       end if
   end tell
   EOF
   ```
   For Terminal.app instead of iTerm, use:
   ```bash
   osascript -e "tell application \"Terminal\" to do script \"conda activate ivrit && python '/path/to/ivrit/main.py' '$1'\""
   ```
7. **Cmd+S**, name it **"Transcribe & Summarize"**

Now right-click any audio file in Finder → **Quick Actions** → **Transcribe & Summarize**. A terminal window opens showing the progress.

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

## macOS Quick Action (right-click menu)

Install a Finder right-click option to transcribe & summarize any audio file:

```bash
bash install_quick_action.sh
```

Then right-click an audio file in Finder → **Quick Actions** → **Transcribe & Summarize**.

## Uninstall

- **Shell alias:** remove the `alias ivrit=...` line from `~/.zshrc`
- **Quick Action:** `rm -rf ~/Library/Services/Transcribe\ \&\ Summarize.workflow`
- **Whisper model cache:** `rm -rf ~/.cache/huggingface/hub/models--ivrit-ai--whisper-large-v3`
- **Conda environment:** `conda remove -n ivrit --all`

## Credits

- [ivrit.ai](https://www.ivrit.ai) for the Hebrew Whisper model and datasets
- [Hugging Face](https://huggingface.co/ivrit-ai/whisper-large-v3) for model hosting
