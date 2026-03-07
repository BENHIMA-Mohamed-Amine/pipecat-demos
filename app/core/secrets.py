from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    nvidia_api_key: str


secrets = Settings(_env_file=".env")
