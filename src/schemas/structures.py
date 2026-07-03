from pydantic import BaseModel, Field
from typing import List, Optional

class ExperienceItem(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class UserProfile(BaseModel):
    name: str = Field(..., description="Display name or full name of the user")
    headline: Optional[str] = Field(None, description="Current professional headline")
    location: Optional[str] = Field(None, description="User location")
    industry: Optional[str] = Field(None, description="Primary industry")
    skills: List[str] = Field(default_factory=list, description="Top skills for outreach and matching")
    goals: Optional[str] = Field(None, description="Long-term career or networking goals")
    summary: Optional[str] = Field(None, description="Personal summary or bio")
    experiences: List[ExperienceItem] = Field(default_factory=list, description="Career history items")
