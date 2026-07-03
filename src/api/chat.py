import os
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

CHAT_ENDPOINT = os.environ.get("CHAT_PROVIDER_URL") or os.environ.get("HERMES_CHAT_ENDPOINT")
CHAT_API_KEY = os.environ.get("CHAT_PROVIDER_API_KEY") or os.environ.get("OPENAI_API_KEY")


@router.post("/chat", response_model=ChatResponse)
def proxy_chat_request(payload: ChatRequest):
    if not CHAT_ENDPOINT:
        raise HTTPException(
            status_code=503,
            detail=(
                "No chat provider is configured. Set CHAT_PROVIDER_URL or HERMES_CHAT_ENDPOINT "
                "in the environment to forward chat requests."
            ),
        )

    headers = {"Content-Type": "application/json"}
    if CHAT_API_KEY:
        headers["Authorization"] = f"Bearer {CHAT_API_KEY}"

    try:
        response = requests.post(CHAT_ENDPOINT, json=payload.dict(), headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    try:
        data = response.json()
    except ValueError:
        data = {"text": response.text}

    text = None
    for key in ("response", "content", "message", "text", "output"):
        if isinstance(data, dict) and key in data:
            value = data[key]
            if isinstance(value, str):
                text = value
                break

    if text is None:
        text = str(data)

    return ChatResponse(response=text, raw_response=data)
