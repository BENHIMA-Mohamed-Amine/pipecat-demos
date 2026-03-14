---
title: I Built a Real-Time Voice AI Agent in ~90 Lines of Python
tags: pipecat, groq, webrtc, voiceagents
---

**TL;DR:** A real-time voice AI agent — STT, LLM, TTS, WebRTC — in ~90 lines using Pipecat and Groq. No custom streaming logic, no callback hell. Just declare the pipeline and run it. [Full code on GitHub](https://github.com/BENHIMA-Mohamed-Amine/pipecat-demos/tree/quickstart)

---

## Why this is hard — and why it's not anymore

Building a real-time voice agent from scratch used to mean writing your own WebRTC server, manual audio streaming pipeline, multiple SDK integrations, and async concurrency management.

Pipecat abstracts all of that. You declare the pipeline, it handles the rest.

---

## The stack

| Layer | Tool |
|---|---|
| Speech-to-Text | Groq (Whisper) |
| Language Model | Groq (LLaMA) |
| Text-to-Speech | Groq (PlayAI) |
| Transport | WebRTC |
| VAD | Silero (local) |
| Framework | Pipecat |

---

## How the pipeline works

Think of it as an assembly line for audio:

```
Microphone
    └─► WebRTC input
            └─► Groq STT (Whisper)
                    └─► User context aggregator (+ Silero VAD)
                                └─► Groq LLM
                                        └─► Groq TTS
                                                └─► WebRTC output
                                                        └─► Assistant context aggregator
```

Each stage processes frames — units of audio, text, or control signals — and passes them downstream.

---

## The code

### 1. Services: plug in Groq

```python
stt = GroqSTTService(api_key=GROQ_API_KEY)
tts = GroqTTSService(api_key=GROQ_API_KEY)
llm = GroqLLMService(api_key=GROQ_API_KEY)
```

### 2. Context: give the bot memory

```python
messages = [
    {
        "role": "system",
        "content": "You are a friendly AI assistant. Respond naturally and keep your answers conversational. Always give short, concise answers — no more than 2-3 sentences.",
    }
]
context = LLMContext(messages)
```

### 3. VAD: the unsung hero

Voice Activity Detection is what determines when the user is done speaking. Without it, the pipeline either waits indefinitely or cuts the user off mid-sentence.

```python
user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
    context,
    user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer())
)
```

Silero VAD runs locally, monitors audio continuously, and fires signals for speech start and stop — triggering the STT stage only after it detects the user has finished speaking.

### 4. The pipeline: declare the flow

```python
pipeline = Pipeline([
    transport.input(),       # Audio in
    stt,                     # Transcribe
    user_aggregator,         # Accumulate + VAD
    llm,                     # Think
    tts,                     # Speak
    transport.output(),      # Audio out
    assistant_aggregator,    # Save response to context
])
```

This reads like the actual data flow — no callbacks, no nesting.

### 5. Events: connect and disconnect

```python
@transport.event_handler("on_client_connected")
async def on_client_connected(transport, client):
    context.add_message(
        {"role": "system", "content": "Say Hello, and briefly introduce yourself."}
    )
    await task.queue_frames([LLMRunFrame()])

@transport.event_handler("on_client_disconnected")
async def client_disconnected(transport, client):
    await task.cancel()
```

On connect, the bot introduces itself. On disconnect, the task cleans up.

---

## Try it yourself

```bash
git clone https://github.com/BENHIMA-Mohamed-Amine/pipecat-demos.git
cd pipecat-demos

uv sync

cp .env.example .env
# Add your GROQ_API_KEY

uv run python main.py
```

Open the browser URL, click Connect, and try: *"Give me some info about Morocco"*

---

## Final thoughts

Pipecat handles WebRTC negotiation, audio buffering, frame scheduling, and async coordination. You get to focus on what the bot does, not how audio moves through the system.

This is what an inflection point looks like for voice AI development.

---

**Full code on GitHub → [pipecat-demos/quickstart](https://github.com/BENHIMA-Mohamed-Amine/pipecat-demos/tree/quickstart)**
