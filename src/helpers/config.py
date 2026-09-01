from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GROQ_API_KEY: str
    VERSION: str
    APP_NAME: str

    FILE_ALLOWED_EXTENSIONS: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE:int

    MONGODB_URL:str
    MONGODB_DATABASE:str

    ## postgres
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID_LITERAL: List[str]
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None

    ## vectordb config
    VECTOR_DB_BACKEND_LITERAL: List[str]
    VECTOR_DB_BACKEND: str = None
    VECTOR_DB_PATH: str = None
    VECTOR_DB_DISTANCE_METHOD: str = None
    DEFAULT_PGVECTOR_INDEX_THRESHOLD:int = None

    # template parser
    PRIMARY_LANG: str
    DEFAULT_LANG: str
@lru_cache()
def get_config() -> Config:
    return Config()
