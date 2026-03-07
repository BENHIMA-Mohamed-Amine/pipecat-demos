from pipecat.pipeline.pipeline import Pipeline
from pipecat.transports.base_transport import BaseTransport

from app.pipeline.factory import PipecatServiceFactory


class VoicePipelineBuilder:
    def __init__(self, factory: PipecatServiceFactory):
        self.factory = factory

    def build(self, transport: BaseTransport):
        stt = self.factory.create_stt()
        llm = self.factory.create_agent()
        tts = self.factory.create_tts()
        context_aggregator_bundle = self.factory.create_context_agg()
        aggregators = context_aggregator_bundle.pair
        context = context_aggregator_bundle.context
        user_agg, assistant_agg = aggregators
        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                user_agg,
                llm,
                tts,
                transport.output(),
                assistant_agg,
            ]
        )

        return pipeline, context
