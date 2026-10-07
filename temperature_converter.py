"""Convert temperatures between Celsius and Fahrenheit."""

unit = input("请输入温度单位（C 表示摄氏度，F 表示华氏度）：").strip().upper()
temperature = float(input("请输入温度数值："))

if unit == "F":
    celsius = (temperature - 32) * 5 / 9
    print(f"摄氏温度：{celsius:.1f} °C")
elif unit == "C":
    fahrenheit = temperature * 9 / 5 + 32
    print(f"华氏温度：{fahrenheit:.1f} °F")
else:
    print("单位输入无效，请输入 C 或 F。")
