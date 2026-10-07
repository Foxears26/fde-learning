"""Manage student names and scores with a list of dictionaries."""

students = []

while True:
    print("\n===== 学生成绩管理系统 =====")
    print("1. 添加学生")
    print("2. 删除学生")
    print("3. 修改分数")
    print("4. 查看所有学生和平均分")
    print("输入 q 退出")

    choice = input("请选择功能：").strip().lower()

    if choice == "q":
        print("已退出成绩管理系统。")
        break

    elif choice == "1":
        name = input("请输入学生姓名：").strip()
        if not name:
            print("姓名不能为空。")
            continue

        try:
            score = float(input("请输入学生分数："))
        except ValueError:
            print("分数请输入数字。")
            continue

        students.append({"name": name, "score": score})
        print(f"已添加学生：{name}")

    elif choice == "2":
        name = input("请输入要删除的学生姓名：").strip()
        for student in students:
            if student["name"] == name:
                students.remove(student)
                print(f"已删除学生：{name}")
                break
        else:
            print(f"没有找到学生：{name}")

    elif choice == "3":
        name = input("请输入要修改分数的学生姓名：").strip()
        for student in students:
            if student["name"] == name:
                try:
                    new_score = float(input("请输入新的分数："))
                except ValueError:
                    print("分数请输入数字。")
                    break

                student["score"] = new_score
                print(f"已更新 {name} 的分数为 {new_score:g}")
                break
        else:
            print(f"没有找到学生：{name}")

    elif choice == "4":
        if not students:
            print("当前没有学生记录，平均分暂时无法计算。")
        else:
            print("\n学生名单：")
            for student in students:
                print(f"姓名：{student['name']}，分数：{student['score']:g}")

            average = sum(student["score"] for student in students) / len(students)
            print(f"平均分：{average:.1f}")

    else:
        print("功能选项无效，请输入 1、2、3、4 或 q。")
