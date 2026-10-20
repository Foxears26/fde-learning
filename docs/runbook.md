# English Version

# Runbook

## Health Check

`curl.exe -H "X-API-Key: dev-secret-key" http://127.0.0.1:8000/alerts` → Should return 200.

## Check Logs

- Local: Check the uvicorn terminal output. To write output to a file when starting the service: `uvicorn main:app > app.log 2>&1`.
- Search by request_id: `Select-String -Path app.log -Pattern "<request_id>"`.
- Container: `docker logs alert-api`.

## Common Issues

1. **401** → Check the X-API-Key value first (typos and extra spaces are the most common causes). Header names are case-insensitive, so there is no need to check their capitalization.
2. **422** → Check loc in detail: level only accepts info/warning/critical; a missing required field is reported as missing.
3. **Port 8000 is already in use** → Run only one of local uvicorn and the Docker container at a time; `docker stop alert-api`.
4. **The container exits immediately after starting** → Check the error with docker logs. A previous incident involved an import name collision (the project folder and a pip package had the same name).
5. **Data is gone** → Known limitation: data is stored in memory and cleared on restart (to be resolved by connecting a database in W6).

---

# Runbook
## 健康检查
curl.exe -H "X-API-Key: dev-secret-key" http://127.0.0.1:8000/alerts → 应返回 200
## 看日志
- 本地：uvicorn 终端输出；落盘启动：uvicorn main:app > app.log 2>&1
- 按 request_id 查：Select-String -Path app.log -Pattern "<request_id>"
- 容器：docker logs alert-api
## 常见故障
1. **401** → 先查 X-API-Key 的值（错一位、带空格最常见），header 名大小写不敏感不用查
2. **422** → 看 detail 里的 loc：level 只收 info/warning/critical；必填字段缺失是 missing
3. **端口 8000 被占用** → 本地 uvicorn 和 Docker 容器只能开一个；docker stop alert-api
4. **容器一起就退** → docker logs 看报错；曾发生 import 撞名（项目文件夹与 pip 包同名）
5. **数据没了** → 已知限制：数据在内存，重启即清（待 W6 接数据库解决）
