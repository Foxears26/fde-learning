"""Extract timestamps and levels, then print only ERROR log lines."""

logs = """\
2026-10-08 13:20:15 [ERROR] Connection timeout
2026-10-08 13:21:03 [INFO] Connection established
2026-10-08 13:22:40 [WARNING] Slow response
2026-10-08 13:23:10 [ERROR] Server unavailable
"""

for line in logs.splitlines():
    parts = line.split()

    # parts[0] 是日期，parts[1] 是时间，parts[2] 是带方括号的级别。
    timestamp = parts[0] + " " + parts[1]
    level = parts[2][1:-1]

    if level == "ERROR":
        print(f"时间：{timestamp}")
        print(f"级别：{level}")
        print(f"日志：{line}")
