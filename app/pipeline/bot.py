from loguru import logger
from pipecat.frames.frames import LLMRunFrame
from pipecat.observers.loggers.metrics_log_observer import MetricsLogObserver
from pipecat.observers.loggers.transcription_log_observer import (
    TranscriptionLogObserver,
)
from pipecat.observers.user_bot_latency_observer import UserBotLatencyObserver
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.base_transport import BaseTransport

from app.pipeline.config import BotConfig
from app.pipeline.pipeline import VoicePipelineBuilder


class VoiceBot:
    def __init__(
        self, transport: BaseTransport, builder: VoicePipelineBuilder, config: BotConfig
    ):
        self.transport = transport
        self.config = config
        pipeline, self.context = builder.build(self.transport)
        self._total_user_bot_observer = UserBotLatencyObserver()
        self.task = PipelineTask(
            pipeline=pipeline,
            params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
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
        @self.transport.event_handler("on_client_connected")
        async def on_connected(_transport, _client):
            logger.info("Client is connected")
            self.context.add_message(
                {"role": "system", "content": self.config.greeting}
            )
            await self.task.queue_frames([LLMRunFrame()])

        @self.transport.event_handler("on_client_disconnected")
        async def on_disconnected(_transport, _client):
            logger.info("Client is disconnected")
            await self.task.cancel()

        @self._total_user_bot_observer.event_handler("on_latency_measured")
        async def on_latency_measured(_total_user_bot_observer, latency):
            logger.info(f"Total latency is {latency:.3f}s")

    async def run(self):
        await PipelineRunner(handle_sigint=False).run(self.task)
