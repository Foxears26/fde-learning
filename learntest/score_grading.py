"""Classify a score using if/elif/else."""

try:
    score = float(input("请输入分数："))
except ValueError:
    print("分数请输入数字。")
else:
    if score >= 90:
        grade = "优秀"
    elif score >= 80:
        grade = "良好"
    elif score >= 60:
        grade = "及格"
    else:
        grade = "不及格"

    print(f"成绩等级：{grade}")
