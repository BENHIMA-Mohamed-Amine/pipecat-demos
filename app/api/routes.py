from fastapi import APIRouter, BackgroundTasks, Depends
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.request_handler import (
    SmallWebRTCPatchRequest,
    SmallWebRTCRequest,
    SmallWebRTCRequestHandler,
)
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

from app.core.contracts import WebRTCAnswer
from app.core.dependencies import get_handler
from app.pipeline.bot import run_bot

router = APIRouter(prefix="/api", tags=["webrtc"])


@router.post("/offer", response_model=WebRTCAnswer)
async def offer(
    request: SmallWebRTCRequest,
    background_tasks: BackgroundTasks,
    small_webrtc_handler: SmallWebRTCRequestHandler = Depends(get_handler),
) -> WebRTCAnswer:
    async def webrtc_connection_callback(connection):
        webrtc_transport = SmallWebRTCTransport(
            webrtc_connection=connection,
            params=TransportParams(
                audio_in_enabled=True, audio_out_enabled=True, audio_out_10ms_chunks=2
            ),
        )
        background_tasks.add_task(run_bot, webrtc_transport)

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
