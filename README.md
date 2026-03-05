# simple-pipecat-bot

A minimal real-time voice agent built with [Pipecat](https://github.com/pipecat-ai/pipecat) and FastAPI.

Streams audio from the browser to the server over WebRTC, runs it through a Gemini Live speech-to-speech pipeline, and streams the response back. No STT, no TTS, no extra hops.

## Stack

- **Pipecat** — voice agent pipeline framework
- **FastAPI** — API server
- **SmallWebRTC** — open source WebRTC transport
- **Gemini Live** — speech-to-speech model
- **Silero VAD + SmartTurn** — turn detection

## Project structure

```
app/
├── api/
│   └── routes.py        # WebRTC offer/ICE endpoints
├── core/
│   ├── contracts.py     # Pydantic models
│   ├── dependencies.py  # Shared handler singleton
│   └── settings.py      # Env config
├── pipeline/
│   └── bot.py           # Pipecat pipeline definition
└── main.py              # FastAPI app entry point
index.html               # Minimal browser client
```

## Setup

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
# Install dependencies
uv sync

# Add your Google API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# Run
uv run python -m app.main
```

Open [http://localhost:3000](http://localhost:3000), click **Connect**, and start talking.

> Make sure you're on localhost. SmallWebRTC requires either localhost or a VM with a public IP. It won't work behind a private VM with a load balancer — use [Daily](https://www.daily.co) in that case.

## How it works

1. Browser sends a WebRTC offer to `/api/offer`
2. Server returns an answer and spins up a pipeline as a background task
3. Audio streams in via WebRTC → VAD → SmartTurn → Gemini Live → audio streams back
4. Each session runs in full isolation, no shared state between users

## Related posts

- [What makes Pipecat different from other voice agent frameworks?](https://dev.to)
- Coming soon: Integrating LangChain with Pipecat
- Coming soon: Streaming transcription and real-time frontend UI