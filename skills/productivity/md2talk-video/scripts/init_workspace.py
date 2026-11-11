#!/usr/bin/env python3
"""Create a talk workspace with an input.md template.

Usage:
    python scripts/init_workspace.py <workspace> [--title TITLE]

The workspace is created under the current directory. Existing input.md is
never overwritten; a partly created workspace can be reused if it has no
input.md yet.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATE = """# {title}

<!--
写作说明（不会进 PPT）：
  ## 是章，### 是页；一页 = 一张幻灯片 + 一段音频 + 一段字幕
  页类型：cover / agenda / section / content / closing，写在 ### 下一行
  连续 > 行是该页的口语稿，一页 40~220 字，念 10~35 秒
  正文是给 PPT 的大纲，2~5 条关键词，不加句号
  围栏代码块和 HTML 注释里的内容不参与切分，可放心放示例
  过渡页（section）标题写章名，过渡词放台词，不放大纲
-->

## 开场

### P01 {title}

<!-- kind: cover -->
> 大家好，这里是《{title}》。接下来几分钟，我们把这件事从头到尾讲清楚，看完你就能自己动手。

- 一句话副标题

## 目录

### P02 今天讲什么

<!-- kind: agenda -->
> 我们分两部分：先讲为什么这件事值得做，再讲具体怎么做，最后给一个能带走、今天就能用上的结论。

- 为什么讲
- 怎么做
- 一个例子
- 结论

## 为什么讲

### P03 为什么讲

<!-- kind: section -->
> 先说清楚问题出在哪，后面的做法才有依据。

### P04 结论先行

<!-- kind: content -->
> 我的判断只有一句：先跑通，再优化。后面每一步都围绕这句话展开，遇到取舍时也按它来。

- 先跑通
- 再优化

### P05 一个例子

<!-- kind: content -->
> 拿一个最小例子走一遍，你会看到它到底解决了什么问题，也能看清哪一步最容易卡住，提前绕开。

- 输入
- 输出

## 怎么做

### P06 怎么做

<!-- kind: section -->
> 接下来拆成两步：先搭骨架，再补细节。

### P07 第一步

<!-- kind: content -->
> 第一步只做骨架，不求完整。骨架立住了，后面加东西才不会返工，也更容易发现方向错了。

- 搭骨架
- 不求完整

### P08 第二步

<!-- kind: content -->
> 第二步补细节。每次只改一处，改完立刻验证，问题不会堆在一起，出问题也能马上定位。

- 一次一处
- 改完就验

### P09 一个常见的坑

<!-- kind: content -->
> 最常见的坑是一开始就追求完美，结果迟迟跑不起来。先让它动起来，再逐步让它变好，这是最省时间的顺序。

- 别追求完美
- 先让它动

## 收尾

### P10 现在就动手

<!-- kind: closing -->
> 别等准备好，挑一个最小任务，今天先跑通一遍。跑通之后，你自然会知道下一步该补什么。

- 挑最小任务
- 今天跑一遍
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="初始化 md2talk-video 工作目录")
    parser.add_argument("workspace", help="工作目录名（相对当前目录）或路径")
    parser.add_argument("--title", default="未命名讲稿", help="文档标题，写进 input.md")
    args = parser.parse_args(argv)

    ws = Path(args.workspace).expanduser().resolve()
    input_md = ws / "input.md"

    if input_md.exists():
        print(f"ERROR input.md 已存在，拒绝覆盖：{input_md}", file=sys.stderr)
        print(f"  hint: 直接编辑它，或用另一个目录名初始化", file=sys.stderr)
        return 2

    try:
        ws.mkdir(parents=True, exist_ok=True)
        input_md.write_text(TEMPLATE.format(title=args.title), encoding="utf-8")
    except OSError as exc:
        print(f"ERROR 创建失败：{exc}", file=sys.stderr)
        return 1

    skill = Path(__file__).resolve().parent.parent
    print(f"已创建工作目录：{ws}")
    print(f"  讲稿模板：{input_md}")
    print()
    print("下一步：")
    print(f"  1. 编辑 {input_md.name}，把模板换成真正的讲稿")
    print(f"  2. {sys.executable} {skill / 'scripts' / 'pipeline.py'} {args.workspace} --review all --from 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
