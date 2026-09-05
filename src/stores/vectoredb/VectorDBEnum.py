from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "qdrant"
    PGVECTOR = "pgvector"

class DistanceMethodEnum(Enum):
    COSINE = "cosine"
    DOT = "dot"
class PgVectorTableSchemeEnums(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"
    
class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_12_ops"

class PgVectorIndexingTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"