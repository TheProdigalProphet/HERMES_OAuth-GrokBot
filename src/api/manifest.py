import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()
MANIFEST_PATH = Path(__file__).resolve().parent.parent.parent / "manifest.json"


@router.get("/manifest")
def get_manifest():
    if not MANIFEST_PATH.exists():
        raise HTTPException(status_code=404, detail="manifest.json not found")

    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
