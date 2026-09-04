from  .providers import QdrantDB, PGVectorDB
from .VectorDBEnum import VectorDBEnum
from controllers.BaseController import BaseController
from sqlalchemy import sessionmaker


class VectorDBProviderFactory():
    def __init__(self, config: dict, db_client: sessionmaker=None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client

    def create(self, provider: str):
        if provider == VectorDBEnum.QDRANT.value:
            return QdrantDB(db_client=self.base_controller.get_db_path(self.config.VECTOR_DB_PATH), distance_method=self.config.VECTOR_DB_DISTANCE_METHOD)
        if provider == VectorDBEnum.PGVECTOR.value:
            return PGVectorDB(db_client=self.db_client, distance_method=self.config.VECTOR_DB_DISTANCE_METHOD, default_vector_size=self.config.VECTOR_DB_DEFAULT_VECTOR_SIZE, default_index_threshold=self.config.DEFAULT_PGVECTOR_INDEX_THRESHOLD)
        return None