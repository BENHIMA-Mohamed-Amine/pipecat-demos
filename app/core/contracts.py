from pydantic import BaseModel


class WebRTCAnswer(BaseModel):
    pc_id: str
    sdp: str
    type: str = "answer"
