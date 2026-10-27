import os
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from api_client import APIClient


router = APIRouter()
REDIRECT_URI = "http://localhost:8000/auth/callback"


@router.get("/login")
async def login():
    params = urlencode({
        "client_id": os.environ["GITHUB_CLIENT_ID"],
        "redirect_uri": REDIRECT_URI,
        "scope": "read:user",
    })
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?{params}", status_code=302
    )


@router.get("/auth/callback")
def auth_callback(code: str):
    # 在请求时读取配置，未配置 OAuth 也不会影响原有接口的启动。
    credentials = {
        "client_id": os.environ["GITHUB_CLIENT_ID"],
        "client_secret": os.environ["GITHUB_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    try:
        with APIClient("https://github.com", timeout=10.0) as client:
            token_response = client.post(
                "/login/oauth/access_token",
                data=credentials,
                headers={"Accept": "application/json"},
            )
            access_token = token_response.json().get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="GitHub authorization failed")

        with APIClient("https://api.github.com", timeout=10.0) as client:
            user_response = client.get(
                "/user",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            username = user_response.json()["login"]
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="GitHub request failed") from None
    except (ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Invalid GitHub response") from None

    return {"login": username, "message": f"欢迎 {username}"}
