# 🎙️ I Built a Real-Time Voice AI Agent in ~90 Lines of Python

> *Speech in. Speech out. No fluff. Just vibes.*

---

## 🧠 What Are We Building?

A **voice AI agent** that:

- 🎤 Listens to you speak
- 📝 Transcribes your words in real time
- 🤖 Thinks with an LLM
- 🔊 Talks back, out loud

All of this, running locally, with [Groq](https://groq.com) and [Pipecat](https://github.com/pipecat-ai/pipecat).

This is my **quickstart into the world of real-time multimodal AI**. And honestly? The code is surprisingly clean.

---

<!-- IMAGE: banner/hero image of the Pipecat Playground UI in action -->

---

## 🤔 Why This Is Hard (and Why It's Not Anymore)

Building a real-time voice agent used to require:

- ❌ Custom WebRTC servers
- ❌ Streaming audio pipelines from scratch
- ❌ Gluing together 5 different SDKs
- ❌ Fighting with async concurrency bugs

Today? A framework called **Pipecat** abstracts all of that away.

You declare a pipeline. You plug in services. It just works.

---

## 🧩 The Stack

| Layer | Tool |
|---|---|
| 🎙️ STT | Groq (Whisper) |
| 🧠 LLM | Groq (LLaMA) |
| 🔊 TTS | Groq (PlayAI) |
| 📡 Transport | WebRTC |
| 🔇 VAD | Silero |
| 🔧 Framework | Pipecat |

Groq is one of the fastest inference providers available, which matters a lot for real-time voice.

---

## 🏗️ How the Pipeline Works

Think of it as an **assembly line for audio**.

```
🎤 Microphone
    └─► 📡 WebRTC input
            └─► 📝 Groq STT (Whisper)
                    └─► 🧩 User Context Aggregator + Silero VAD
                                └─► 🧠 Groq LLM
                                        └─► 🔊 Groq TTS
                                                └─► 📡 WebRTC output
                                                        └─► 🧩 Assistant Context Aggregator
```

Each stage is a **processor** that receives frames, transforms them, and passes them downstream.

> 💡 A "frame" in Pipecat is just a unit of data: audio bytes, text, or a signal to trigger the LLM.

The magic of Pipecat is that **you don't manage this flow manually**. You declare it, and the framework handles scheduling, buffering, and async coordination.

---

## 👁️ VAD: The Unsung Hero

**Voice Activity Detection (VAD)** is what makes the bot feel responsive.

Without VAD, the pipeline wouldn't know when you've finished speaking. It would either:
- Wait forever ⏳
- Cut you off mid-sentence ✂️

**Silero VAD** listens to the audio stream continuously. It fires a signal when you **start** speaking, and another when you **stop**. Only after the stop signal does the pipeline forward your speech to STT.

```python
user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
    context,
    user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer())
)
```

One line. Fully streaming VAD. That's the abstraction Pipecat gives you. 🙌

---

## 🧑‍💻 The Code: Let's Walk Through It

The full bot lives in a single file: `main.py`. Let's break it down.

### 1️⃣ Services: Plug in Groq

```python
stt = GroqSTTService(api_key=GROQ_API_KEY)
tts = GroqTTSService(api_key=GROQ_API_KEY)
llm = GroqLLMService(api_key=GROQ_API_KEY)
```

Three services, three lines. STT, TTS, LLM. All running on Groq.

---

### 2️⃣ Context: Give the Bot a Memory

```python
messages = [
    {
        "role": "system",
        "content": "You are a friendly AI assistant. Respond naturally and keep your answers conversational. Always give short, concise answers — no more than 2-3 sentences.",
    }
]

context = LLMContext(messages)
```

This is the **conversation history**. Every turn (user speech and bot response) gets appended here automatically by the aggregators.

The system prompt is where you shape the bot's personality. Short sentences, direct tone, no essays. ✅

---

### 3️⃣ The Pipeline: Declare the Flow

```python
pipeline = Pipeline([
    transport.input(),       # 🎤 Audio in
    stt,                     # 📝 Transcribe
    user_aggregator,         # 🧩 Accumulate + VAD
    llm,                     # 🧠 Think
    tts,                     # 🔊 Speak
    transport.output(),      # 📡 Audio out
    assistant_aggregator,    # 🧩 Save response to context
])
```

Read it top to bottom. That's literally the data flow. Clean. Declarative. No callbacks spaghetti.

---

### 4️⃣ Events: Connect and Disconnect

```python
@transport.event_handler("on_client_connected")
async def on_client_connected(transport, client):
    context.add_message(
        {"role": "system", "content": "Say Hello, and briefly introduce yourself."}
    )
    await task.queue_frames([LLMRunFrame()])
```

When a client connects, we inject a message into the context and **trigger the LLM manually** with `LLMRunFrame()`. This fires the greeting before the user says anything.

```python
@transport.event_handler("on_client_disconnected")
async def client_disconnected(transport, client):
    await task.cancel()
```

On disconnect: clean shutdown. No zombie pipelines. 🧹

> ⚠️ Common mistake: registering `on_client_disconnected` on `task` instead of `transport`. The event lives on the transport. Get this wrong and the handler silently never fires.

---

### 5️⃣ Run It

```python
runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
await runner.run(task)
```

The runner manages the lifecycle of the task: starts it, keeps it alive, handles signals.

---

## 🚀 Try It Yourself

```bash
git clone https://github.com/BENHIMA-Mohamed-Amine/pipecat-demos.git
cd pipecat-demos

uv sync

cp .env.example .env
# Add your GROQ_API_KEY

uv run python main.py
```

Open the URL printed in your terminal, click **Connect** in the top-right corner, and say:

> *"Give me some info about Morocco"* 🇲🇦

<!-- IMAGE: screenshot of the Pipecat Playground UI mid-conversation -->

---

## 🔭 What's Next?

This is just the beginning.

The bot you just built runs locally, using Pipecat's built-in WebRTC playground. Great for prototyping. Not production.

**In the next post**, we'll go deeper:

- 🐍 Wrap the bot in a **FastAPI** web app
- 📦 Expose a proper `/connect` endpoint
- 🌐 Replace the toy client with a real frontend
- 🚢 Make it deployable

The architecture shifts from a script to a **service**. That's where it gets real.

---

## 💬 Final Thoughts

What strikes me most about this stack is how much complexity Pipecat hides.

WebRTC negotiation, audio buffering, frame scheduling, async pipelines. All gone. You write business logic. The framework handles the plumbing.

That's the right abstraction level for building **production-grade real-time AI agents**.

We're genuinely at an inflection point. The tools are here. The APIs are accessible.

There's never been a better time to build voice AI. 🎙️

---

*Follow along for Part 2: FastAPI + Pipecat for production deployments.*

---

**Tags:** `#AI` `#VoiceAI` `#Python` `#Pipecat` `#Groq` `#WebRTC` `#MachineLearning` `#RealtimeAI` `#LLM` `#BuildInPublic`
