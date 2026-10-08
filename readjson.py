import json

try:
    with open("alert.json", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print("文件不存在")
except json.JSONDecodeError:
    print("文件内容不是合法 JSON")