# 默认主题占位

`config/default.yaml` 把 `ppt.theme` 指到这里，并通过命令模板的 `{theme}` 传给
ppt-master。真正的主题资源（字体、配色、版式、母版）各工具格式不同，所以这里只留
一个可解析的目录，不预设格式。

接真实 ppt-master 时，二选一：

1. 把主题包放进本目录，覆盖 `README.md` 之外的资源；
2. 或改 `config/default.yaml` 的 `ppt.theme`，指向你自己的主题目录（相对路径先按
   skill 目录解析，再按工作目录解析）。

HTML PPT 始终落在 `<workspace>/out/3_htmlppt/pNNN.html`，所以即使主题不完美，也
可以在 GATE 3 直接改 HTML 继续出片。
