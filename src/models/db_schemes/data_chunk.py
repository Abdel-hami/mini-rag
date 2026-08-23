from pydantic import BaseModel, ConfigDict, Field
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_content: str = Field(...,min_length=1)
    chunk_metadata: dict
    chun_order: int= Field(...,gt=0) ## ... means that this field is required 
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    @classmethod
    def get_indexes(cls):
    
            return [
                {
                    "key":[ ("chunk_project_id", 1)],
                    "name": "chunk_project_id_index_1",
                    "unique": False
                }
            ]

class RetrievedDocument(BaseModel):
    text: str 
    score: float
    ## then we can add metadata and so on