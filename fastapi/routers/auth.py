import os
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse


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
async def auth_callback(code: str):
    # 在请求时读取配置，未配置 OAuth 也不会影响原有接口的启动。
    credentials = {
        "client_id": os.environ["GITHUB_CLIENT_ID"],
        "client_secret": os.environ["GITHUB_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data=credentials,
                headers={"Accept": "application/json"},
            )
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="GitHub authorization failed")

            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_response.raise_for_status()
            username = user_response.json()["login"]
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="GitHub request failed") from None
    except (ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Invalid GitHub response") from None

    return {"login": username, "message": f"欢迎 {username}"}
