from providers.QdrantDB import QdrantDB
from VectorDBEnum import VectorDBEnum
from controllers.BaseController import BaseController
class VectorDBProviderFactory():
    def __init__(self, config: dict):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        if provider == VectorDBEnum.QDRANT.value:
            return QdrantDB(db_path=self.base_controller.get_db_path(self.config.VECTOR_DB_PATH), distance_method=self.config.VECTOR_DB_DISTANCE_METHOD)
        return None