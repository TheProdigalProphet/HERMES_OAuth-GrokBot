from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class BackgroundDocumentRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    title: str = Field(..., description="Document title or heading")
    category: str = Field(..., description="Document category: experience, documentation, career_direction, profile_note")
    content: str = Field(..., description="Full document text or entry content")

class BackgroundDocument(BackgroundDocumentRequest):
    model_config = ConfigDict(extra='ignore')
    id: str = Field(..., description="Unique document identifier")
    created_at: str = Field(..., description="UTC creation timestamp")

class EvidenceItemRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    title: str = Field(..., description="Evidence item title")
    category: str = Field(
        ...,
        description="Evidence category: DCP Interaction, Church/Faith, Relapse Prevention, Housing, Career, Legal, Contact with Leo, etc."
    )
    description: str = Field(..., description="Detailed evidence description")
    date: Optional[str] = Field(None, description="Date of the event or evidence item")
    due_date: Optional[str] = Field(None, description="Associated due date for the evidence item")
    status: Optional[str] = Field("open", description="Current status of the evidence item")
    risk_level: Optional[str] = Field("medium", description="Risk level for this item")
    follow_up: Optional[str] = Field(None, description="Follow-up action required")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering and grouping evidence items")
    faith_support: Optional[bool] = Field(False, description="Whether this item tracks faith or church support")
    contact_type: Optional[str] = Field(None, description="Type of contact or interaction")

class EvidenceItem(EvidenceItemRequest):
    model_config = ConfigDict(extra='ignore')
    id: str = Field(..., description="Unique evidence item identifier")
    created_at: str = Field(..., description="UTC timestamp when item was created")

class EvidenceReportRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    month: Optional[int] = Field(None, description="Optional month for the report")
    year: Optional[int] = Field(None, description="Optional year for the report")
    note: Optional[str] = Field(None, description="Optional note for the generated report")

class EvidenceReportResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    report_summary: str
    metrics: dict

class EliteProfileResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    profile: dict
    background_documents: List[BackgroundDocument]
    elite_summary: str
