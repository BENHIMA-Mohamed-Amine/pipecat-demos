from langchain.agents import AgentState
from langchain_core.runnables import Runnable
from pipecat.pipeline.pipeline import Pipeline
from pipecat.transports.base_transport import BaseTransport

from app.core.types import ContextAggregatorBundle
from app.pipeline.factory import PipecatServiceFactory


class VoicePipelineBuilder:
    def __init__(
        self,
        factory: PipecatServiceFactory,
        agent: Runnable,
        state: AgentState,
        thread_id: str,
    ):
        self.factory = factory
        self.agent = agent
        self.state = state
        self.thread_id = thread_id

    def build(self, transport: BaseTransport) -> tuple[Pipeline, ContextAggregatorBundle]:
        stt = self.factory.create_stt()
        agent = self.factory.create_agent(self.agent, self.state, self.thread_id)
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
