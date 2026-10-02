
Day：W1D1
今天主题：Python的安装和环境

1. 今天做了什么 Today we are learning the installation of Python. We build and activate the virtual environments, then we install VSCode and Python as extensions. Finally, we build a new Python file and run it successfully

2. 关键代码逐行讲

把今天手敲的关键代码贴进来，逐行说明它在干什么：

python -m venv .venv
.venv\Scripts\activate
This is the first line:
1. The first 'python' is the Python we just installed.
2. The '-m' means make these modules run as a program.
3. 'venv' means it's a Python standard module to create a virtual environment.
4. The '.venv' is the folder's name.
The second line is the start script, which belongs to Python. After I rerun the second line, 它修改当前终端的 PATH，让 python/pip 指向虚拟环境里的那一套。not the global system

# 你的代码，每行后面写注释解释

3. 报错复盘（今天每个报错都记一条）

#报错现象（贴关键信息）我第一反应猜的实际根因怎么修的下次怎么避免1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Taxation policy 本身就是一个命令。我们之前运行的 PS1 脚本是被禁止的，所以我们现在把它设置成 RemoteSigned。

这里有几个安全的档位：
1. Restricted：什么脚本都不让跑，也就是默认的。
2. AllSigned：必须有签名的脚本才能跑。
3. RemoteSigned：本地创建的可以跑，从网上下载的还是不能跑，比较适合现在的开发者模式。
4. Unrestricted：什么都让跑，这样就特别的不安全。

后面的参数就是这个设置影响的范围。所以我们现在设置成的是 CurrentUser，也就是现在我们用的这个用户。

4. AI 帮我写的部分——我真懂了吗

AI 写了哪几段：都是ai写的



如果 AI 不在，我能自己写出来吗？（诚实打分 1–5）：1

5. 对照今天的验收项

把计划里的验收标准抄过来，逐项打勾：

Python 3.11 装好，python --version / pip --version 正常
虚拟环境建好并激活，pip install requests 成功
VS Code + Microsoft Python 插件装好，终端自动激活 .venv（还顺手修了 PowerShell 执行策略）
能写能跑 Python 文件


未通过的项 + 补救计划：na

6. 提交

commit message：没有

已 push 到 GitHub：是 / 否



