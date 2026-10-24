sequenceDiagram
    participant B as 浏览器
    participant A as 你的后端
    participant G as GitHub
    B->>A: GET /login
    A->>B: 302 跳转到 github.com/login/oauth/authorize
    B->>G: 用户点 Authorize（同意授权）
    G->>B: 302 回调 /auth/callback?code=xxx
    B->>A: GET /auth/callback?code=xxx
    A->>G: POST /login/oauth/access_token（code + client_secret）
    G->>A: access_token + refresh_token
    A->>G: GET /api/user（Authorization: Bearer token）
    G->>A: 用户信息
    A->>B: {"login": "Foxears26", "message": "欢迎 Foxears26"}