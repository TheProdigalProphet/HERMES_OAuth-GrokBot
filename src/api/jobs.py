from fastapi import APIRouter
from src.api.profile import load_profile

router = APIRouter()

@router.get("/match")
def match_jobs():
    profile = load_profile()
    return {
        "profile_summary": f"{profile.name} | {profile.headline} | {profile.location}",
        "match_hint": "Use the constant user profile to rank job opportunities and personalize outreach.",
        "recommended_jobs": [
            {
                "title": "Senior AI Product Manager",
                "company": "Example AI Inc.",
                "reason": "Strong match for skills and product leadership goals."
            }
        ]
    }
