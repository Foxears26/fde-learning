"""Practice a three-attempt password check with a while loop."""


def check_login():
    """Allow up to three password attempts."""
    password = "123456"
    attempts = 0

    while attempts < 3:
        entered_password = input("请输入密码：")
        attempts += 1

        if entered_password == password:
            print("登录成功")
            break
        else:
            print(f"密码错误，还剩 {3 - attempts} 次机会。")
    else:
        print("已锁定")


if __name__ == "__main__":
    check_login()
