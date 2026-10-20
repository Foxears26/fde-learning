"""A simple calculator that keeps running until the user quits."""

while True:
    first_input = input("请输入第一个数字（输入 Q 退出）：").strip()
    if first_input.lower() == "q":
        print("已退出计算器。")
        break

    try:
        number1 = float(first_input)
        number2 = float(input("请输入第二个数字："))
    except ValueError:
        print("输入无效，请输入数字。")
        continue

    operator = input("请输入运算符（+、-、*、/）：").strip()

    if operator == "+":
        result = number1 + number2
    elif operator == "-":
        result = number1 - number2
    elif operator == "*":
        result = number1 * number2
    elif operator == "/":
        if number2 == 0:
            print("错误：除数不能为 0。")
            continue
        result = number1 / number2
    else:
        print("无效的运算符，请输入 +、-、* 或 /。")
        continue

    print(f"计算结果：{result}")
