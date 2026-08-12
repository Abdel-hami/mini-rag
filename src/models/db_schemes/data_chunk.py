from pydantic import BaseModel, ConfigDict, Field
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _id: Optional[ObjectId]
    chunk_content: str = Field(...,min_length=1)
    chunk_metadata: dict
    chun_order: int= Field(...,gt=0) ## ... means that this field is required
    chunk_project_id: ObjectId