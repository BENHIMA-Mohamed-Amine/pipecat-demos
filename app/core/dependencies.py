from langchain.agents import AgentState
from pipecat.transports.smallwebrtc.request_handler import SmallWebRTCRequestHandler

from app.core.secrets import secrets
from app.langchain_agent.agent import LangchainAgent
from app.pipeline.factory import PipecatServiceFactory
from app.pipeline.pipeline import VoicePipelineBuilder

small_webrtc_handler = SmallWebRTCRequestHandler()


def get_handler() -> SmallWebRTCRequestHandler:
    return small_webrtc_handler


def get_pipeline_builder() -> VoicePipelineBuilder:
    agent = LangchainAgent(secrets).create()
    factory = PipecatServiceFactory(secrets)
    state = AgentState()
    return VoicePipelineBuilder(factory, agent, state, "test")
