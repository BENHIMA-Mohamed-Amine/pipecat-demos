from fastapi import APIRouter, BackgroundTasks, Depends
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.request_handler import (
    SmallWebRTCPatchRequest,
    SmallWebRTCRequest,
    SmallWebRTCRequestHandler,
)
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

from app.core.dependencies import get_handler, get_pipeline_builder
from app.core.schemas import WebRTCAnswer
from app.pipeline.bot import VoiceBot
from app.pipeline.config import BotConfig
from app.pipeline.pipeline import VoicePipelineBuilder

router = APIRouter(prefix="/api", tags=["webrtc"])


@router.post("/offer", response_model=WebRTCAnswer)
async def offer(
    request: SmallWebRTCRequest,
    background_tasks: BackgroundTasks,
    small_webrtc_handler: SmallWebRTCRequestHandler = Depends(get_handler),
    pipe_builder: VoicePipelineBuilder = Depends(get_pipeline_builder),
) -> WebRTCAnswer:
    bot_config = BotConfig()

    async def webrtc_connection_callback(connection):
        webrtc_transport = SmallWebRTCTransport(
            webrtc_connection=connection,
            params=TransportParams(
                audio_in_enabled=True, audio_out_enabled=True, audio_out_10ms_chunks=2
            ),
        )
        bot = VoiceBot(webrtc_transport, pipe_builder, bot_config)
        background_tasks.add_task(bot.run)

    answer = await small_webrtc_handler.handle_web_request(
        request=request, webrtc_connection_callback=webrtc_connection_callback
    )

    return WebRTCAnswer(**answer)


@router.patch("/offer")
async def ice_candidate(
    request: SmallWebRTCPatchRequest,
    small_webrtc_handler: SmallWebRTCRequestHandler = Depends(get_handler),
):
    await small_webrtc_handler.handle_patch_request(request)
    return {"status": "success"}
