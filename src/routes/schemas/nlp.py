from pydantic import BaseModel

class NLPPushRequest(BaseModel):
    do_reset: bool