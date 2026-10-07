"""Guess a randomly chosen number from 1 to 100."""

import random

secret_number = random.randint(1, 100)
guess_count = 0

while True:
    try:
        guess = int(input("猜一个 1 到 100 的整数："))
    except ValueError:
        print("请输入整数。")
        continue

    guess_count += 1

    if guess < secret_number:
        print("小了，再猜一次。")
    elif guess > secret_number:
        print("大了，再猜一次。")
    else:
        print(f"猜中了！你一共猜了 {guess_count} 次。")
        break
