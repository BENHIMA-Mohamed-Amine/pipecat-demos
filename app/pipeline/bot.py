from loguru import logger
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import (
    LocalSmartTurnAnalyzerV3,
)
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.observers.user_bot_latency_observer import UserBotLatencyObserver
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.google.gemini_live.llm import (
    ContextWindowCompressionParams,
    GeminiLiveLLMService,
    InputParams,
)
from pipecat.transcriptions.language import Language
from pipecat.transports.base_transport import BaseTransport
from pipecat.turns.user_stop import TurnAnalyzerUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies

from app.core.settings import config

SYSTEM_INSTRUCTION = f"""
"You are Gemini Chatbot, a friendly, helpful robot.

Your goal is to demonstrate your capabilities in a succinct way.

Your output will be converted to audio so don't include special characters in your answers.

Respond to what the user said in a creative and helpful way. Keep your responses brief. One or two sentences at most.
"""

latency_observer = UserBotLatencyObserver()


async def run_bot(transport: BaseTransport):

    llm = GeminiLiveLLMService(
        api_key=config.google_api_key,
        system_instruction=SYSTEM_INSTRUCTION,
        params=InputParams(
            temperature=0.7,
            max_tokens=2048,
            language=Language.EN_US,
            context_window_compression=ContextWindowCompressionParams(enabled=True)
        ),
    )

    context = LLMContext(
        [
            {
                "role": "user",
                "content": "Start by greeting the user warmly and introducing yourself.",
            }
        ]
    )

    stop_strategy = TurnAnalyzerUserTurnStopStrategy(
        turn_analyzer=LocalSmartTurnAnalyzerV3(params=SmartTurnParams(stop_secs=2)),
        timeout=0.3,
    )

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context=context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
            user_turn_strategies=UserTurnStrategies(stop=[stop_strategy]),
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            user_aggregator,
            llm,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline=pipeline,
        params=PipelineParams(
            enable_metrics=True, enable_usage_metrics=True, observers=[latency_observer]
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Pipecat Client connected")
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(tranport, client):
        logger.info("Pipecat Client disconnected")
        await task.cancel()

    @latency_observer.event_handler("on_latency_measured")
    async def on_latency_measured(observer, latency):
        logger.debug(f"User-to-bot latency: {latency:.3f}s")

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
