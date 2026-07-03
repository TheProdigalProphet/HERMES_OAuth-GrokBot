from pydantic import BaseModel, Field
from typing import Any, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="The chat prompt or message to send to the upstream provider.")
    use_background: Optional[bool] = Field(False, description="Whether the chat should use background documents or agent context.")
    profile_aware: Optional[bool] = Field(False, description="Whether the chat should factor in the synced user profile.")
    metadata: Optional[dict] = Field(None, description="Optional metadata or context for the chat request.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The text response returned by the upstream chat provider.")
    raw_response: Optional[Any] = Field(None, description="The original upstream provider response payload.")
