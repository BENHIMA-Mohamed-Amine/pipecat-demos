import os

from dotenv import load_dotenv
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.groq.stt import GroqSTTService
from pipecat.services.groq.tts import GroqTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams

load_dotenv(override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    stt = GroqSTTService(api_key=GROQ_API_KEY)
    tts = GroqTTSService(api_key=GROQ_API_KEY)
    llm = GroqLLMService(api_key=GROQ_API_KEY)

    messages = [
        {
            "role": "system",
            "content": "You are a friendly AI assistant. Respond naturally and keep your answers conversational. Always give short, concise answers — no more than 2-3 sentences.",
        }
    ]

    context = LLMContext(messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context, user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer())
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline, params=PipelineParams(enable_metrics=True, enable_usage_metrics=True)
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        print("Client Connected")
        context.add_message(
            {"role": "system", "content": "Say Hello, and briefly introduce yourself."}
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def client_disconnected(transport, client):
        print("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):

    transport_params = {
        "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True)
    }

    transport = await create_transport(runner_args, transport_params)

    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
