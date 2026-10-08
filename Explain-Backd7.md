Day：W1D7
今天主题：Python 函数与返回值、字符串方法、JSON 文件读写、类和对象、日志文本处理

1. 今天做了什么

- 理解函数里的 `return`：把函数计算出的结果交还给调用者；没有 `return` 时，函数调用结果默认是 `None`。
- 学习字符串的 `join()`：用一个字符串作为分隔符，连接字符串序列中的内容。
- 在 `utils.py` 中整理可复用的小函数：温度转换、偶数判断、字符串反转、平均值、三数最大值、元音计数、阶乘、质数判断、去重和单词计数。
- 讨论了 `factorial()` 和 `is_prime()` 的实现思路，包括循环、取余、输入检查和返回值。
- 新建 `testw2d5.py`，用 `split()` 和切片从多行日志中提取时间和级别，并只输出 `ERROR` 日志。
- 编写 `readjson.py`，使用 `json.load()` 读取 JSON 文件，并处理文件不存在和 JSON 格式错误。
- 编写 `classAlert.py`，定义 `Alert` 类，实现对象转字典、保存为 JSON、从 JSON 文件读取并重新创建对象。

2. 关键代码逐行讲

日志解析：

```python
parts = line.split()
timestamp = parts[0] + " " + parts[1]
level = parts[2][1:-1]

if level == "ERROR":
    print(f"时间：{timestamp}")
    print(f"级别：{level}")
    print(f"日志：{line}")
```

- `split()` 默认按空白字符拆分一行日志。
- `parts[0]` 是日期，`parts[1]` 是时间，两者中间加空格后组成完整时间。
- `parts[2]` 是带方括号的级别，例如 `[ERROR]`；`[1:-1]` 切掉第一个和最后一个字符，得到 `ERROR`。
- `if level == "ERROR"` 只让错误级别的日志进入打印代码。
- f-string 把提取出的变量值插入输出文本。

JSON 与 `Alert` 类的关键代码：

```python
def to_dict(self):
    return {"level": self.level, "title": self.title, "time": self.time}

def save(self, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

@classmethod
def load(cls, path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return cls(data["level"], data["title"], data["time"])
```

- `to_dict(self)` 把对象的三个属性整理成字典；`self.level` 等表示当前对象的属性。
- `save(self, path)` 用 `with open(..., "w")` 打开文件进行写入；`json.dump()` 把字典写成 JSON。`ensure_ascii=False` 让中文直接保存为中文，`indent=2` 让文件缩进更易读。
- `@classmethod` 把下面的方法声明为类方法，因此第一个参数是类本身 `cls`。
- `load(cls, path)` 用 `json.load()` 从文件读取 JSON 字典，再通过 `cls(...)` 创建并返回一个 `Alert` 对象。
- `readjson.py` 中的 `try` 包住文件读取；`except FileNotFoundError` 处理找不到文件，`except json.JSONDecodeError` 处理文件内容不是合法 JSON。

3. 报错复盘（今天每个报错都记一条）

待留意的问题：`readjson.py` 成功读取后把内容放进 `data`，但目前没有打印或继续使用它；可以在读取成功后加 `print(data)` 来查看结果。运行 `classAlert.py` 时会写入 `alert.json`，需要确保运行目录正确且有写入权限。

4. AI 帮我写的部分——我真懂了吗

AI 写了哪几段：

- `utils.py` 中新增的工具函数实现。
- `testw2d5.py` 中多行日志的拆分、切片和 ERROR 筛选逻辑。
- 今天的记录根据我对 `readjson.py` 和 `classAlert.py` 文件内容的阅读整理

每段在干什么（逐段讲）：

- 工具函数把小任务封装起来供其他代码调用。`factorial()` 用循环累乘；`is_prime()` 检查 2 到平方根范围内是否有整除因数；`average()` 把总和除以数量；其他函数分别做字符串反转、最大值、元音计数、去重和单词计数。
- 日志脚本把每行按空格拆开，组合日期和时间，从 `[ERROR]` 中切出级别，再用条件判断过滤日志。
- `readjson.py` 把 JSON 文件转换为 Python 数据，并针对两种读取错误给出提示。
- `Alert` 类把告警数据放在对象属性中，通过字典和 JSON 在对象与文件之间转换。

我亲手改了什么、为什么改：

今天没有记录对 AI 生成代码进行修改。 `readjson.py` 和 `classAlert.py`；可补充其中遇到的具体问题或自行调整的代码。

如果 AI 不在，我能自己写出来吗？（诚实打分 1–5）：

自评分数：2 / 5。建议分别尝试独立写出一个简单工具函数、日志解析循环，以及 JSON 文件读写

5. 对照今天的验收项

把计划里的验收标准抄过来，逐项打勾：


6. 提交



已 push 到 GitHub：y

