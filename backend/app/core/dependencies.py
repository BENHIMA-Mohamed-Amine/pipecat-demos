from fastapi import Request
from langchain_core.runnables import Runnable
from pipecat.transports.smallwebrtc.request_handler import SmallWebRTCRequestHandler

from app.core.secrets import secrets
from app.pipeline.factory import PipecatServiceFactory
from app.pipeline.pipeline import VoicePipelineBuilder

small_webrtc_handler = SmallWebRTCRequestHandler()


def get_handler() -> SmallWebRTCRequestHandler:
    return small_webrtc_handler


def get_agent(request: Request) -> Runnable:
    return request.app.state.agent


def get_pipeline_builder() -> VoicePipelineBuilder:
    factory = PipecatServiceFactory(secrets)
    return VoicePipelineBuilder(factory)
