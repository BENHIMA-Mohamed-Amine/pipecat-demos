import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from loguru import logger

from app.api.routes import router as webrtc_router
from app.core.secrets import secrets

if secrets.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = secrets.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = secrets.langsmith_project

from app.core.dependencies import small_webrtc_handler
from app.langchain_agent.agent import LangchainAgent
from app.langchain_agent.load_index import LoadAndIndex
from app.langchain_agent.retriever_tool import RetrieverTool


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            api_key=secrets.nvidia_api_key,
        )
        # Initialize the LoadAndIndex class, load documents and create the vector store with indexed documents
        loader = LoadAndIndex(
            file_path=secrets.rag_file_path,
            embeddings=embeddings,
            url=secrets.qdrant_url,
            collection_name=secrets.qdrant_collection_name,
        )
        await loader.load_and_index()
        app.state.vector_store = loader.vector_store
        # Initialize the retriever tool with the created vector store and pass it to the agent
        # This allows the agent to use the retriever tool for fetching relevant information from the vector store during conversations
        retriever_tool = RetrieverTool(vector_store=app.state.vector_store, k=5)
        app.state.agent = LangchainAgent(
            secrets, tools=[retriever_tool.retriever_tool]
        ).create()
    except Exception:
        logger.exception("Error occurred during lifespan")
        raise
    yield
    await small_webrtc_handler.close()


app = FastAPI(title="Pipecat with Fastapi", lifespan=lifespan)
app.include_router(webrtc_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def serve_index():
    return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run(app="app.main:app", port=3000, host="localhost", reload=False)
