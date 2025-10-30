from pydantic import BaseModel, Field

class InvokeRequest(BaseModel):
    input: str = Field(..., description='instructions')


class InvokeResponse(BaseModel):
    message: str    