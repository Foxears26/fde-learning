Day：W1D3
今天主题：GitHub + 分支。

1. 今天做了什么
  今天我们学了如何将本地的 repo push 到远程仓库：

    a. SSH 配置：
    我们要先学习 SSH 的配置，配置完了才可以建立连接，将本地的代码 push 到远程仓库。

    b. 分支与冲突处理：
    我们学了如何建立分支。当在分支和 main 之间同时修改同一个文件时，会出现一些冲突。我们故意制造了一些冲突，并且将它手动合并了。

2. 关键代码逐行讲

ssh-keygen -t ed25519 -C "welcomerobin@gmail.com"
这是我们来建立一个新的SSH
cat ~/.ssh/id_ed25519.pub
我们复制公钥,将其复制到 GitHub 上,这就像是一把锁.我们手底下还有一个同名但不是以 .pub 结尾的文件,那个是私钥,需要我们自己保管
git remote add origin git@github.com:foxears/fde-learning.git
git push -u origin master
这个是将我们本地的仓库和远程的仓库连接在一起,然后我们 push 本地的代码作为 master
git switch -c feature-greeting

git checkout master

git merge feature-greeting

git log --oneline --graph
git branch -d feature-greeting
git push


3. 报错复盘（今天每个报错都记一条）

#报错现象（贴关键信息）我第一反应猜的实际根因怎么修的下次怎么避免1
PS F:\Downloads\daily study\10.2\fde-learning> git push -u origin master
ERROR: Repository not found.
fatal: Could not read from remote repository.
Please make sure you have the correct access rights
and the repository exists.


5. 对照今天的验收项

把计划里的验收标准抄过来，逐项打勾：

done! SSH 配通（还顺手处理了 known_hosts 旧钥匙报警） 
done! fde-learning 推上 GitHub，本地远程已同步
done! 亲手制造并解决了一次合并冲突，看懂 --graph 分叉图
done! 搞清了 switch/checkout 新老写法、master/main 名字问题



6. 提交

commit message：

已 push 到 GitHub：是 



