# Real-Time Voice Agent with NVIDIA NIM + Pipecat

A full-stack voice agent that runs entirely on NVIDIA NIM's free tier - no credit card, no infrastructure, one API key. STT → LLM → TTS over WebRTC, with VAD, smart turn detection, and idle reminders out of the box.

> Built to answer one question: *is NVIDIA NIM's free tier good enough for a real-time voice agent demo?*
> [Read the full breakdown →](https://dev.to/mohamedamine_benhima/is-nvidia-nims-free-tier-good-enough-for-a-real-time-voice-agent-demo-2fa1)

---

## About

Every voice agent tutorial starts with "add your OpenAI API key" - and you've burned $20 before validating a single idea. NVIDIA NIM gives you hosted STT, LLM, and TTS under one free API key (40 RPM, no credit card). This project wires it into Pipecat and ships a production-quality feature set: voice activity detection, smart turn detection, and idle reminders - in a single weekend build.

The demo runs a French-speaking Moroccan travel guide bot, but the pipeline is generic and easy to reconfigure.

---

## Features

- **Full NVIDIA NIM stack** - Whisper Large v3 (STT), Llama 3.3 70B Instruct (LLM), Riva TTS - one API key
- **WebRTC audio transport** - browser to server, no mic button needed
- **Silero VAD** - local voice activity detection, starts listening automatically
- **SmartTurn v3** - local model that understands whether the user finished speaking or just paused mid-sentence
- **Idle reminder hook** - bot gently prompts the user after 60s of silence, no polling
- **Session isolation** - each WebRTC connection runs in full isolation, no shared state between users
- **Honest benchmarks** - STT, LLM, and TTS latency measured and documented

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Pipeline framework | [Pipecat](https://github.com/pipecat-ai/pipecat) |
| Web server | FastAPI + Uvicorn |
| Audio transport | SmallWebRTC |
| STT | NVIDIA NIM - Whisper Large v3 |
| LLM | NVIDIA NIM - Meta Llama 3.3 70B Instruct |
| TTS | NVIDIA NIM - Riva TTS |
| VAD | Silero (local) |
| Turn detection | LocalSmartTurnAnalyzerV3 (local) |
| Package manager | [uv](https://github.com/astral-sh/uv) |

---

## Getting Started

**Prerequisites:** Python 3.12+, [uv](https://github.com/astral-sh/uv), an [NVIDIA NIM API key](https://build.nvidia.com)

```bash
# Install dependencies
uv sync

# Add your NVIDIA API key
echo "NVIDIA_API_KEY=your_key_here" > .env

# Run
uv run python -m app.main
```

Open [http://localhost:3000](http://localhost:3000), click **Connect**, and start talking.

> **Note:** SmallWebRTC requires either localhost or a VM with a public IP. It won't work behind a private VM with a load balancer - use [Daily](https://www.daily.co) in that case.

---

## Project Structure

```
app/
├── api/
│   └── routes.py          # WebRTC offer/ICE endpoints
├── core/
│   ├── dependencies.py    # Shared handler singleton
│   ├── schemas.py         # Pydantic response models
│   ├── secrets.py         # Env config (NVIDIA API key)
│   └── types.py           # Shared types
├── pipeline/
│   ├── bot.py             # VoiceBot - event handlers, pipeline runner
│   ├── config.py          # Bot persona and system prompt
│   ├── factory.py         # NVIDIA service instantiation
│   └── pipeline.py        # Pipeline assembly (STT → LLM → TTS)
└── main.py                # FastAPI app entry point
index.html                 # Minimal browser client
```

---

## Usage

The pipeline is defined in 7 lines:

```python
pipeline = Pipeline([
    transport.input(),
    stt, user_agg, llm, tts,
    transport.output(),
    assistant_agg,
])
```

To change the bot persona, edit [app/pipeline/config.py](app/pipeline/config.py):

```python
@dataclass
class BotConfig:
    greeting: str = "Please introduce yourself to the user."
    system_prompt: str = "You are a ..."
```

---

## Known Limitations

- **NVIDIA streaming STT is English-only.** Passing `fr-FR` to the cloud endpoint silently fails - NVIDIA truncates the locale internally and can't match a model. This is a cloud infrastructure bug, not a Pipecat issue. Workaround: `NvidiaSegmentedSTTService` with Whisper Large v3 (~1s latency vs ~200ms for streaming).
- **LLM latency is inconsistent.** Turn-to-turn variance is too high for a snappy conversation experience. Not production-ready as-is.
- **SmallWebRTC requires localhost or a public IP.** Won't work behind a private VM + load balancer.
- **Free tier cap: 40 RPM.** Enough for demos and iteration, not for concurrent users.

---

## Author

**Mohamed Amine Benhima**

- [LinkedIn](https://www.linkedin.com/in/mohamed-amine-benhima/)
- [Blog post: Is NVIDIA NIM's free tier good enough for a real-time voice agent demo?](https://dev.to/mohamedamine_benhima/is-nvidia-nims-free-tier-good-enough-for-a-real-time-voice-agent-demo-2fa1)
