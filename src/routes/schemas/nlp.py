from pydantic import BaseModel
from typing import Optional
class NLPPushRequest(BaseModel):
    do_reset: bool

class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5