# 如何在vscode中编译latex？

* 安装插件latex workshop
* 编写tex文件
* 执行 `command + shift + p`命令，点击 `LaTex Workshop: Build with recipe`
* 会出现好几个编译命令
  * `latexmk`：主要用于编译英文pdf
  * `latexmk(xelatex)`：主要用于编译包含中文latex，会出现中间文件xdv
