from fastapi import APIRouter
from pydantic import BaseModel
from src.api.profile import load_profile

router = APIRouter()

class OutreachRequest(BaseModel):
    target_name: str
    role: str
    company: str


@router.post("/outreach")
def generate_outreach(request: OutreachRequest):
    profile = load_profile()
    return {
        "target": request.target_name,
        "message": (
            f"Hi {request.target_name},\n\n"
            f"I noticed your work as a {request.role} at {request.company} and thought our shared interests in {', '.join(profile.skills[:3]) or 'professional growth'} could be a great reason to connect. "
            f"As someone with a background in {profile.industry or 'technology'} and a goal of {profile.goals or 'building meaningful partnerships'}, I’d love to learn more about your approach.\n\n"
            f"Thanks,\n{profile.name}"
        ),
        "profile_context": profile.dict()
    }
