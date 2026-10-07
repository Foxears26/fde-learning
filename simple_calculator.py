"""A simple calculator for two numbers."""

number1 = float(input("请输入第一个数字："))
operator = input("请输入运算符（+、-、*、/）：").strip()
number2 = float(input("请输入第二个数字："))

if operator == "+":
    result = number1 + number2
elif operator == "-":
    result = number1 - number2
elif operator == "*":
    result = number1 * number2
elif operator == "/":
    if number2 == 0:
        print("错误：除数不能为 0。")
    else:
        result = number1 / number2
else:
    print("无效的运算符，请输入 +、-、* 或 /。")

if operator in ("+", "-", "*") or (operator == "/" and number2 != 0):
    print(f"计算结果：{result}")
