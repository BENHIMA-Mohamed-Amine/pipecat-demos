from pipecat.transports.smallwebrtc.request_handler import SmallWebRTCRequestHandler

small_webrtc_handler = SmallWebRTCRequestHandler()


def get_handler() -> SmallWebRTCRequestHandler:
    return small_webrtc_handler
