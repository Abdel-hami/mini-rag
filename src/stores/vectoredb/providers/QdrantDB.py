from VectorDBInterface import VectorDBInterface
from VectorDBEnum import VectorDBEnum,DistanceMethodEnum
from qdrant_client import QdrantClient, models
import logging

class QdrantDB(VectorDBInterface):

    def __init__(self, db_path:str, distance_method:str):

        self.client =  None
        self.db_path = db_path
        self.distance_method = None
        
        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(self.db_path)