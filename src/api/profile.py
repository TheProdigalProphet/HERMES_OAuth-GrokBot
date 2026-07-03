import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.schemas.structures import UserProfile

router = APIRouter()
PROFILE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "user_profile.json"
PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_profile() -> UserProfile:
    if PROFILE_PATH.exists():
        data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        return UserProfile.parse_obj(data)
    return UserProfile(
        name="",
        headline="",
        location="",
        industry="",
        skills=[],
        goals="",
        summary="",
    )


def save_profile(profile: UserProfile) -> None:
    PROFILE_PATH.write_text(profile.model_dump_json(indent=2), encoding="utf-8")


@router.get("", response_model=UserProfile)
def get_profile():
    return load_profile()


@router.post("", response_model=UserProfile)
def update_profile(profile: UserProfile):
    try:
        save_profile(profile)
        return profile
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
