import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.profile import load_profile, save_profile
from src.schemas.background import BackgroundDocumentRequest, BackgroundDocument, EliteProfileResponse
from src.schemas.structures import ExperienceItem, UserProfile

router = APIRouter()
BACKGROUND_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "background"
BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)


class BackgroundDocumentPayload(BackgroundDocumentRequest):
    pass


def document_path(doc_id: str) -> Path:
    return BACKGROUND_DIR / f"{doc_id}.json"


def load_all_documents() -> List[BackgroundDocument]:
    docs = []
    for path in sorted(BACKGROUND_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        docs.append(BackgroundDocument.parse_obj(data))
    return docs


def extract_company(content: str) -> str:
    patterns = [r"\bat\s+([A-Z][\w&\-,. ]+)", r"\bwith\s+([A-Z][\w&\-,. ]+)"]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            company = match.group(1).strip()
            return company.split("\n")[0].strip()
    return "Unknown"


def extract_goal(content: str) -> str:
    patterns = [
        r"goal is to ([^.\n]+)",
        r"goal is ([^.\n]+)",
        r"aims? to ([^.\n]+)",
        r"seeks? to ([^.\n]+)",
        r"looking to ([^.\n]+)",
        r"want(s| to) ([^.\n]+)",
        r"aspire(s| to) ([^.\n]+)",
        r"seeking ([^.\n]+)",
    ]
    lowered = content.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return match.group(0).capitalize().strip()
    return ""


def extract_summary(content: str) -> str:
    summary = content.strip().split("\n")[0]
    if "." in summary:
        summary = summary.split(".")[0].strip() + "."
    return summary


def append_unique_summary(profile: UserProfile, statement: str) -> None:
    if not statement:
        return
    current = profile.summary or ""
    if statement not in current:
        if current:
            profile.summary = f"{current}\n\n{statement}"
        else:
            profile.summary = statement


def update_profile_from_document(profile: UserProfile, document: BackgroundDocument) -> None:
    category = document.category.lower().strip()
    statement = ""

    if category == "experience":
        company = extract_company(document.content)
        if not any(exp.title == document.title and exp.company == company for exp in profile.experiences):
            profile.experiences.append(
                ExperienceItem(
                    title=document.title,
                    company=company,
                    description=document.content,
                )
            )
        statement = f"Added experience '{document.title}' at {company}."

    elif category == "career_direction":
        goal = extract_goal(document.content) or document.content.strip()
        profile.goals = goal
        statement = f"Updated career direction: {goal}"

    elif category in {"documentation", "profile_note"}:
        statement = f"Added background note: {extract_summary(document.content)}"

    else:
        statement = f"Incorporated background content: {extract_summary(document.content)}"

    append_unique_summary(profile, statement)
    save_profile(profile)


def build_elite_profile(profile: UserProfile, documents: List[BackgroundDocument]) -> dict:
    aggregated = {
        "name": profile.name,
        "headline": profile.headline,
        "location": profile.location,
        "industry": profile.industry,
        "skills": profile.skills,
        "goals": profile.goals,
        "summary": profile.summary,
        "experiences": [exp.dict() for exp in profile.experiences],
        "background_insights": [doc.content for doc in documents],
    }
    if documents:
        aggregated["elite_summary"] = (
            "This elite profile combines the user's career history, documentation, and direction entries "
            "into a concise, high-impact narrative for Hermes reasoning."
        )
    else:
        aggregated["elite_summary"] = "No background documents have been added yet."

    return aggregated


@router.post("/background/document", response_model=BackgroundDocument)
def add_background_document(payload: BackgroundDocumentPayload):
    doc_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    document = BackgroundDocument(
        id=doc_id,
        title=payload.title,
        category=payload.category,
        content=payload.content,
        created_at=now,
    )
    document_path(doc_id).write_text(document.model_dump_json(indent=2), encoding="utf-8")

    profile = load_profile()
    update_profile_from_document(profile, document)
    return document


@router.get("/background/documents", response_model=List[BackgroundDocument])
def get_background_documents():
    return load_all_documents()


@router.post("/background/elitesummary", response_model=EliteProfileResponse)
def generate_elite_profile():
    profile = load_profile()
    documents = load_all_documents()
    elite_summary = (
        "Hermes has synthesized the user's profile and all background documents into an elite profile summary. "
        "This summary is ideal for personalized outreach, networking, and career positioning."
    )
    return EliteProfileResponse(
        profile=profile.dict(),
        background_documents=documents,
        elite_summary=elite_summary,
    )


@router.post("/background/sync-profile", response_model=UserProfile)
def sync_profile_from_documents():
    profile = load_profile()
    documents = load_all_documents()
    for document in documents:
        update_profile_from_document(profile, document)
    return profile
