Day：W1D2
今天主题：

1. 今天做了什么
我们这节课学了 Git 的基础应用,安装了 Git.在 Git 中有 3 个非常重要的概念：Working Directory,Staging Area 和Local repository.之后我们学的那一些命令,都是跟如何将文件在这三个区域中转换有关.比如说,我们要先创建一个 initial 的 repository,这样就会有一个仓库.在这之前,我们需要建立一个 .gitignore 文件,将虚拟环境的相关文件都忽略掉之后,我们才应该再建本地的仓库.因为如果不先忽略掉虚拟环境,你建立的仓库就已经包括了那个环境本身,后面再建也没有用了之后我们就可以用到了：
1. 先用 git status 查看一下这个仓库的状态。
2. 然后我们可以用 git add 这样的命令，将工作区的内容先存到暂存区。
3. 存到暂存区后，我们可以使用 git commit -m 将暂存区的内容添加到本地仓库。
4. 其中，我们还可以使用 git diff 来查看同一文件在不同工作区,暂存区或仓库之间的 difference

Git reset 命令就是将本地仓库的文件调回工作区或者暂存区。reset 分为三种模式：soft、mixed 和 hard。
1. soft 模式：工作区和暂存区的内容都会保留。
2. mixed 模式：只会保留工作区的内容，暂存区的内容不会保留。
3. hard 模式：工作区和暂存区的内容都不会保留。

最后我们列了一下删除的操作：
1. 先建了一个 temp.txt 文档。
2. 将其 add 和 commit，把这个文件放到本地仓库中。
3. 之后，使用 git rm 加文件名，将工作区和暂存区的这个文件都删除掉。

2. 关键代码逐行讲

把今天手敲的关键代码贴进来，逐行说明它在干什么：
git status
git diff
git add hello.py
git commit -m "W1D2: add second print line"

git reset --soft HEAD~1
git log --oneline
git status

temp" | Out-File temp.txt
git add temp.txt
git commit -m "W1D2: add temp file for rm demo"
git rm temp.txt
git status
git commit -m "W1D2: remove temp file via git rm"

3. 报错复盘（今天每个报错都记一条）

na

4.

5. 对照今天的验收项

把计划里的验收标准抄过来，逐项打勾：
 Git for Windows 装好，user.name/user.email 配置成 GitHub 那套
 fde-learning 建仓，.gitignore 先行，.venv 没进仓库
 git log --oneline 5 次提交，message 条条有信息量
 工作区 / 暂存区 / 版本库三区模型 + git status / git diff 会用
 git reset --soft 后悔药体验过，--hard 知道是危险品
 git rm 和手删的区别亲手验证过

6. 提交

commit message：na

已 push 到 GitHub：否


