from langchain_core.runnables import Runnable
from pipecat.pipeline.pipeline import Pipeline
from pipecat.transports.base_transport import BaseTransport

from app.core.types import ContextAggregatorBundle
from app.pipeline.factory import PipecatServiceFactory


class VoicePipelineBuilder:
    def __init__(self, factory: PipecatServiceFactory):
        self.factory = factory

    def build(
        self,
        transport: BaseTransport,
        agent: Runnable,
        thread_id: str,
    ) -> tuple[Pipeline, ContextAggregatorBundle]:
        stt = self.factory.create_stt()
        agent = self.factory.create_agent(agent, thread_id)
        tts = self.factory.create_tts()
        bundle = self.factory.create_context_agg()
        user_agg, assistant_agg = bundle.pair
        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                user_agg,
                agent,
                tts,
                transport.output(),
                assistant_agg,
            ]
        )

        return pipeline, bundle
