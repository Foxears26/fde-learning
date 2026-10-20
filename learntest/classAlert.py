import json

class Alert:
    def __init__(self, level, title, time):  # 构造函数，创建对象时传这三个
        self.level = level
        self.title = title
        self.time = time

    def to_dict(self):                       # 转成字典，JSON 只认字典
        return {"level": self.level, "title": self.title, "time": self.time}

    def save(self, path):                    # 写文件：对象 → 字典 → JSON → 硬盘
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path):                     # 读文件：硬盘 → JSON → 字典 → 对象
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(data["level"], data["title"], data["time"])


a = Alert("ERROR", "连接超时", "2026-10-09 13:20:15")
a.save("alert.json")          # 存盘
b = Alert.load("alert.json")  # 读回，b 和 a 内容一样
print(b.title)                # 验证