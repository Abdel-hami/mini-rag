from pydantic import BaseModel, ConfigDict, Field
from bson.objectid import ObjectId
from typing import Optional

class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow", populate_by_name=True)
    
    id: Optional[ObjectId] = Field(default=None,alias="_id")
    project_id: str
