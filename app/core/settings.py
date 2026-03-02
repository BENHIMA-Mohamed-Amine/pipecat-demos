from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str


config = Settings(_env_file=".env")
