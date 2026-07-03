import os
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from urllib.parse import urlencode

from src.schemas.auth import AuthStatusResponse, AuthGrantResponse

router = APIRouter()

OAUTH_STATE = "hermes-web-auth-state"
AUTH_STORE = {
    "authorized": False,
    "provider": None,
    "account": None,
    "access_token": None,
}


class OAuthConfig(BaseModel):
    client_id: str
    authorize_url: str
    token_url: str
    redirect_uri: str
    scopes: str
    provider: str


def get_oauth_config() -> OAuthConfig:
    return OAuthConfig(
        client_id=os.environ.get("OAUTH_CLIENT_ID", "your-client-id"),
        authorize_url=os.environ.get("OAUTH_AUTHORIZE_URL", "https://example.com/oauth/authorize"),
        token_url=os.environ.get("OAUTH_TOKEN_URL", "https://example.com/oauth/token"),
        redirect_uri=os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback"),
        scopes=os.environ.get("OAUTH_SCOPES", "openid profile email"),
        provider=os.environ.get("OAUTH_PROVIDER", "example"),
    )


@router.get("/auth/start")
def auth_start(config: OAuthConfig = Depends(get_oauth_config)):
    query = {
        "response_type": "code",
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": config.scopes,
        "state": OAUTH_STATE,
    }
    url = f"{config.authorize_url}?{urlencode(query)}"
    return RedirectResponse(url)


@router.get("/auth/callback")
def auth_callback(request: Request, config: OAuthConfig = Depends(get_oauth_config)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if state != OAUTH_STATE or not code:
        raise HTTPException(status_code=400, detail="Invalid OAuth callback response")

    AUTH_STORE.update(
        {
            "authorized": True,
            "provider": config.provider,
            "account": "user@example.com",
            "access_token": "fake-token-for-demo",
        }
    )
    return {"status": "authorized", "account": AUTH_STORE["account"]}


@router.get("/auth/status", response_model=AuthStatusResponse)
def auth_status():
    return AuthStatusResponse(
        authorized=AUTH_STORE["authorized"],
        provider=AUTH_STORE["provider"],
        account=AUTH_STORE["account"],
        access_token=AUTH_STORE["access_token"],
        note="Use /auth/start to begin browser-based authorization.",
    )


@router.post("/auth/revoke", response_model=AuthGrantResponse)
def auth_revoke():
    AUTH_STORE.update(
        {
            "authorized": False,
            "provider": None,
            "account": None,
            "access_token": None,
        }
    )
    return AuthGrantResponse(
        authorized=False,
        account=None,
        access_token=None,
        message="Authorization revoked.",
    )
