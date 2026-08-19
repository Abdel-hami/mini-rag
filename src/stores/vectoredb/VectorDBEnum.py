from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "qdrant"

class DistanceMethodEnum(Enum):
    COSINE = "cosine"
    DOT = "dot"