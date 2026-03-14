from langchain_core.runnables import Runnable
from loguru import logger
from pipecat.frames.frames import LLMMessagesAppendFrame, LLMRunFrame
from pipecat.observers.loggers.metrics_log_observer import MetricsLogObserver
from pipecat.observers.loggers.transcription_log_observer import (
    TranscriptionLogObserver,
)
from pipecat.observers.user_bot_latency_observer import UserBotLatencyObserver
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response_universal import LLMUserAggregator
from pipecat.processors.frameworks.rtvi import RTVIObserverParams
from pipecat.transports.base_transport import BaseTransport

from app.pipeline.config import BotConfig
from app.pipeline.pipeline import VoicePipelineBuilder


class VoiceBot:
    def __init__(
        self,
        transport: BaseTransport,
        builder: VoicePipelineBuilder,
        config: BotConfig,
        agent: Runnable,
        thread_id: str,
    ):
        self._transport = transport
        self._config = config
        pipeline, bundle = builder.build(self._transport, agent, thread_id)
        self.context = bundle.context
        self._user_agg = bundle.pair.user()
        self._total_user_bot_observer = UserBotLatencyObserver()
        self._task = PipelineTask(
            pipeline=pipeline,
            params=PipelineParams(enable_metrics=True, enable_usage_metrics=True, report_only_initial_ttfb=True),
            rtvi_observer_params=RTVIObserverParams(
                bot_audio_level_enabled=True,
            ),
            observers=[
                self._total_user_bot_observer,
                TranscriptionLogObserver(),
                MetricsLogObserver(),
            ],
            enable_tracing=True,
            enable_turn_tracking=True,
        )
        self._register_handlers()

    def _register_handlers(self):
        @self._transport.event_handler("on_client_connected")
        async def on_connected(_transport, _client):
            logger.info("Client is connected")
            self.context.add_message(
                {"role": "system", "content": self._config.greeting}
            )
            await self._task.queue_frames([LLMRunFrame()])

        @self._transport.event_handler("on_client_disconnected")
        async def on_disconnected(_transport, _client):
            logger.info("Client is disconnected")
            await self._task.cancel()

        @self._total_user_bot_observer.event_handler("on_latency_measured")
        async def on_latency_measured(_total_user_bot_observer, latency):
            logger.info(f"Total latency is {latency:.3f}s")

        @self._user_agg.event_handler("on_user_turn_idle")
        async def on_user_idle(aggregator: LLMUserAggregator):
            await aggregator.push_frame(
                LLMMessagesAppendFrame(
                    messages=[
                        {
                            "role": "user",
                            "content": "The user has been idle. Gently remind them you're here to help.",
                        }
                    ],
                    run_llm=True,
                )
            )

    async def run(self):
        try:
            await PipelineRunner(handle_sigint=False).run(self._task)
        except Exception:
            logger.exception("Error running pipeline")
