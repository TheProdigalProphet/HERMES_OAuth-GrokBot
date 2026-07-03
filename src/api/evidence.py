import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from src.schemas.background import EvidenceItemRequest, EvidenceItem, EvidenceReportRequest, EvidenceReportResponse

router = APIRouter()
EVIDENCE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def evidence_path(item_id: str) -> Path:
    return EVIDENCE_DIR / f"{item_id}.json"


def load_all_evidence() -> List[EvidenceItem]:
    items: List[EvidenceItem] = []
    for path in sorted(EVIDENCE_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items.append(EvidenceItem.parse_obj(data))
    return items


@router.post("/evidence/item", response_model=EvidenceItem)
def add_evidence_item(payload: EvidenceItemRequest):
    item_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    item = EvidenceItem(
        id=item_id,
        created_at=now,
        title=payload.title,
        category=payload.category,
        description=payload.description,
        date=payload.date,
        due_date=payload.due_date,
        status=payload.status,
        risk_level=payload.risk_level,
        follow_up=payload.follow_up,
        tags=payload.tags,
        faith_support=payload.faith_support,
        contact_type=payload.contact_type,
    )
    evidence_path(item_id).write_text(item.model_dump_json(indent=2), encoding="utf-8")
    return item


@router.get("/evidence/items", response_model=List[EvidenceItem])
def list_evidence_items():
    return load_all_evidence()


@router.get("/evidence/metrics", response_model=EvidenceReportResponse)
def evidence_metrics():
    items = load_all_evidence()
    count = len(items)
    category_counts = {}
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    status_counts = {}

    for item in items:
        category_counts[item.category] = category_counts.get(item.category, 0) + 1
        if item.risk_level:
            normalized = item.risk_level.lower()
            if normalized in risk_counts:
                risk_counts[normalized] += 1
        status_counts[item.status] = status_counts.get(item.status, 0) + 1

    report = EvidenceReportResponse(
        report_summary=f"Tracked {count} evidence items in the dashboard.",
        metrics={
            "total_items": count,
            "category_counts": category_counts,
            "risk_counts": risk_counts,
            "status_counts": status_counts,
        },
    )
    return report


@router.post("/evidence/report", response_model=EvidenceReportResponse)
def generate_evidence_report(payload: EvidenceReportRequest):
    items = load_all_evidence()
    count = len(items)
    report_summary = (
        f"Monthly evidence report generated for "
        f"{payload.month}/{payload.year}. "
        f"{count} tracked items included. "
        f"Note: {payload.note or 'No additional note.'}"
    )
    report = EvidenceReportResponse(
        report_summary=report_summary,
        metrics={
            "total_items": count,
            "month": payload.month,
            "year": payload.year,
            "note": payload.note,
        },
    )
    return report
