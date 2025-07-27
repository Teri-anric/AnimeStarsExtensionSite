from pydantic import BaseModel
from uuid import UUID

class WsDataBase(BaseModel):
    pass

class WsEventBase(BaseModel):
    id: UUID | None = None
    event: str
    data: WsDataBase | None = None

class WsResponseBase(BaseModel):
    id: UUID | None = None
    success: bool
    error: str | None = None
    data: WsDataBase | None = None
