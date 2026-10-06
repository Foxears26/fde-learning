Day：W1D5 
今天主题：Codex 桌面版

1. 今天做了什么
今天我们安装了 ChatGPT 的桌面版，并在 Codex 里新建了一个任务。

a. 初始任务与运行：
我们让它在仓库的根目录新建一个叫 hello.py 的文件，写一个 greet 函数，要求返回 hello.name，并带上 docstring 和 main 的示例。写完以后让它运行，把结果截图给我看。

b. 学习与迭代步骤：
我们要学习的就是这个制作的步骤：
(a) 编写与审核：让它来写，写完我们就来审它的 diff。
(b) 要求返工：看完以后，我们要求它返工。在返工时，我们让它在 greet 函数里加上类型注解，并规定如果 name 是空字符串，就返回 hello stranger。
(c) 持续迭代：之后我们再看它返回的结果和 diff，如果不满意就追着让它改，看它一点一点迭代。
2. 关键代码逐行讲

把今天手敲的关键代码贴进来，逐行说明它在干什么：
def greet(name: str) -> str:

    """Return a friendly greeting for the given name."""

    if name == "":

        return "Hello, stranger!"

    return f"Hello, {name}!"



if __name__ == "__main__":

    print(greet("World"))

这个就是他写的啊：

我们先定义一个 greet 函数，输入的函数参数是 name。name 是一个字符串，我们需要它返回字符串，后面是一个文档。

然后我们来判断 name 这个参数是否为空：
a. 如果为空，我们就返回 "hello stranger"；
b. 否则，我们就返回 "hello" 加上这个函数参数。

后面我们会写上一个运行的示例，打印的是 greet 这个函数，然后将 "world" 传参到 name 上。



3. 报错复盘（今天每个报错都记一条）

git add . 把 .pyc 带进去了，根因是没写 .gitignore，以后新仓库先写 ignore 再 add

4. AI 帮我写的部分——我真懂了吗

类型注解是它加的，我自己还写不利索,diff 我能看懂，但让我自己从零写 greet 我还得想想

5. 对照今天的验收项
done! 函数签名：name: str 参数、-> str 返回值，docstring 是干嘛的讲清了
done! 空字符串分支逻辑讲清了
done! if __name__ == "__main__" 的作用讲对了（直接运行才执行，import 时不执行）


6. 提交


已 push 到 GitHub：是 


