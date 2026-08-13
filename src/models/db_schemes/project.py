from pydantic import BaseModel, ConfigDict, Field
from bson.objectid import ObjectId
from typing import Optional

class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow", populate_by_name=True)
    # populate_by_name=True: it means that if you have a field in the model with the same name as a key in the input dict, it will be populated
    #just means: let me construct the model using either the alias (_id=...) or the real name (id=...) — otherwise Pydantic would only accept the alias.
    
    id: Optional[ObjectId] = Field(default=None,alias="_id") # translation rule: incoming/outgoing key _id ↔ Python attribute id
    #alias is used to change the name of the field because _id is a reserved word
    # it's something like "when you see _id in the input dict, put it in the id field"
    project_id: str

    # id vs project_id
    # It's like the difference between a username you pick when signing up versus an internal database row number the system assigns you — one is yours to set, the other only exists once the system has actually created the row.