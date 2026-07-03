from pydantic import BaseModel
from typing import Optional

class AuthStatusResponse(BaseModel):
    authorized: bool
    provider: Optional[str] = None
    account: Optional[str] = None
    access_token: Optional[str] = None
    note: Optional[str] = None

class AuthGrantResponse(BaseModel):
    authorized: bool
    account: Optional[str] = None
    access_token: Optional[str] = None
    message: str
