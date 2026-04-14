import sys
import time
import json
import urllib.request

from config import LLM_PROVIDER, GEMINI_API_KEY, CLAUDE_API_KEY, OLLAMA_MODEL

SUMMARY_PROMPT = """
You are an expert meeting analyst. Below is a raw transcript from a meeting (may be in Hebrew or mixed Hebrew/English).

Your tasks:
1. Identify speakers — even without formal diarization, infer speaker changes from context, questions/answers, name mentions, topic shifts. Label them Speaker A, Speaker B, etc. (or use real names if mentioned).
2. Produce a structured meeting summary in the SAME LANGUAGE as the transcript (Hebrew if Hebrew, English if English):

---
## Speakers Identified
List each inferred speaker and brief description of their role/contribution.

## General Summary
2-4 sentences capturing the meeting's purpose and outcome.

## Action Items
Bullet list. Each item: WHO needs to do WHAT by WHEN (if mentioned).

## Key Decisions
Bullet list of decisions made during the meeting.

## Important Topics Discussed
Bullet list of major themes or topics.

## Open Questions / Unresolved Items
Anything left undecided or requiring follow-up.
---

Transcript:
{transcript}
"""


def _call_gemini(model: str, prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["candidates"][0]["content"]["parts"][0]["text"]


def summarize_gemini(transcript: str) -> str:
    prompt = SUMMARY_PROMPT.format(transcript=transcript)

    try:
        print("  Trying gemini-2.5-flash...")
        return _call_gemini("gemini-2.5-flash", prompt)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  Rate limited, falling back to gemini-2.5-flash-lite...")
            return _call_gemini("gemini-2.5-flash-lite", prompt)
        raise


def summarize_claude(transcript: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    prompt = SUMMARY_PROMPT.format(transcript=transcript)

    payload = json.dumps({
        "model": "claude-sonnet-4-5-20241022",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["content"][0]["text"]


def summarize_ollama(transcript: str) -> str:
    url = "http://localhost:11434/api/generate"
    prompt = SUMMARY_PROMPT.format(transcript=transcript)

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["response"]


def summarize(transcript: str) -> str:
    print(f"\nSummarizing with: {LLM_PROVIDER}...")
    t = time.time()

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY not set in .env file")
            sys.exit(1)
        result = summarize_gemini(transcript)
    elif LLM_PROVIDER == "claude":
        if not CLAUDE_API_KEY:
            print("Error: CLAUDE_API_KEY not set in .env file")
            sys.exit(1)
        result = summarize_claude(transcript)
    elif LLM_PROVIDER == "ollama":
        result = summarize_ollama(transcript)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. Choose gemini / claude / ollama")

    print(f"Summary generated in {time.time() - t:.1f}s")
    return f'<div dir="rtl">\n\n{result}\n\n</div>'


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <transcript_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        transcript = f.read()

    summary = summarize(transcript)
    print("\n--- Meeting Summary ---")
    print(summary)
