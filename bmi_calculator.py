"""Calculate BMI from height in centimeters and weight in kilograms."""

height_cm = float(input("请输入身高（厘米）："))
weight = float(input("请输入体重（千克）："))

height_m = height_cm / 100
bmi = weight / (height_m ** 2)

if bmi < 18.5:
    category = "偏瘦"
elif bmi <= 24:
    category = "正常"
else:
    category = "偏胖"

print(f"你的 BMI 是：{bmi:.1f}")
print(f"判断结果：{category}")
