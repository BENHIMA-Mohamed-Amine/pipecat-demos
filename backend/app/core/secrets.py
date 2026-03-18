from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    nvidia_api_key: str = ""
    groq_api_key: str = ""
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "novamark_services"
    rag_file_path: str = "./data/rag.csv"
    langsmith_api_key: str = ""
    langsmith_project: str = "pipecat-langchain"


secrets = Settings(_env_file=".env")
