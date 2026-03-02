from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from pipecat.transports.smallwebrtc.request_handler import SmallWebRTCRequestHandler

from app.api.routes import router as webrtc_router
from app.core.dependencies import small_webrtc_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await small_webrtc_handler.close()


app = FastAPI(title="Pipecat with Fastapi", lifespan=lifespan)
app.include_router(webrtc_router)


@app.get("/")
async def serve_index():
    return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run(app="app.main:app", port=3000, host="0.0.0.0", reload=True)
