"""Fast regression tests for the md2talk-video skill.

Run:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))

import builtin_ppt  # noqa: E402
import deck_check  # noqa: E402
import md_parse  # noqa: E402
import pipeline  # noqa: E402
import ppt  # noqa: E402

DECK = """# 测试

## 开场
### P01 封面
<!-- kind: cover -->
> 大家好，今天用几分钟把这件事讲清楚，看完就能上手。
- 副标题

## 目录
### P02 目录
<!-- kind: agenda -->
> 我们分两部分：先讲为什么，再讲怎么做。
- 为什么
- 怎么做
- 两步
- 结论

## 为什么
### P03 为什么
<!-- kind: section -->
> 先说清楚问题出在哪。

### P04 结论
<!-- kind: content -->
> 我的判断只有一句：先跑通，再优化，后面每一步都围绕它。
- 先跑通
- 再优化

### P05 例子
<!-- kind: content -->
> 拿一个最小例子走一遍，你会看到它到底解决了什么问题。
- 输入
- 输出

## 怎么做
### P06 怎么做
<!-- kind: section -->
> 接下来拆成两步：先搭骨架，再补细节。

### P07 第一步
<!-- kind: content -->
> 第一步只做骨架，不求完整，骨架立住后面才不会返工。
- 搭骨架
- 不求完整

### P08 第二步
<!-- kind: content -->
> 第二步补细节，每次只改一处，改完立刻验证。
- 一次一处
- 改完就验

### P09 一个常见的坑
<!-- kind: content -->
> 最常见的坑是一开始就追求完美，结果迟迟跑不起来。
- 别追求完美
- 先让它动

## 收尾
### P10 现在就动手
<!-- kind: closing -->
> 别等准备好，挑一个最小任务，今天先跑通一遍。
- 挑最小任务
- 今天跑一遍
"""


class ParseTests(unittest.TestCase):
    def parse(self, text: str) -> dict:
        tmp = Path(tempfile.mkdtemp())
        src = tmp / "input.md"
        src.write_text(text, encoding="utf-8")
        return md_parse.parse(src)

    def test_fenced_markdown_does_not_split_pages(self):
        text = DECK.replace(
            "- 先跑通\n- 再优化",
            "- 先跑通\n- 再优化\n\n```markdown\n## 假章节\n### 假页面\n> 假台词\n```",
        )
        parsed = self.parse(text)
        self.assertEqual(len(parsed["chapters"]), 5)
        self.assertEqual(len(parsed["pages"]), 10)
        self.assertIn("假章节", parsed["pages"][3]["code"])
        self.assertNotIn("假章节", [c["title"] for c in parsed["chapters"]])

    def test_kind_and_code_are_captured(self):
        parsed = self.parse(DECK)
        kinds = [p["kind"] for p in parsed["pages"]]
        self.assertEqual(kinds[0], "cover")
        self.assertEqual(kinds[2], "section")
        self.assertEqual(kinds[-1], "closing")


class DeckCheckTests(unittest.TestCase):
    def parse(self, text: str) -> dict:
        tmp = Path(tempfile.mkdtemp())
        src = tmp / "input.md"
        src.write_text(text, encoding="utf-8")
        return md_parse.parse(src)

    def test_good_deck_has_no_errors(self):
        issues = deck_check.audit(self.parse(DECK))
        self.assertEqual([i for i in issues if i["level"] == "error"], [])

    def test_section_with_bullets_warns(self):
        text = DECK.replace(
            "> 先说清楚问题出在哪。\n",
            "> 先说清楚问题出在哪。\n\n- 不该有要点\n",
        )
        issues = deck_check.audit(self.parse(text))
        self.assertTrue(any("过渡页" in i["message"] for i in issues))

    def test_section_title_too_long_warns(self):
        text = DECK.replace("### P03 为什么", "### P03 这是一个明显过长的章节过渡页标题")
        issues = deck_check.audit(self.parse(text))
        self.assertTrue(any("过渡页标题" in i["message"] for i in issues))


class ArtifactTests(unittest.TestCase):
    def test_fingerprint_changes_with_speech(self):
        a = pipeline._fingerprint("tts", "同一句话", "edge-tts", "v", "+0%")
        b = pipeline._fingerprint("tts", "换一句话", "edge-tts", "v", "+0%")
        self.assertNotEqual(a, b)

    def test_builtin_strips_page_number_and_scales(self):
        page = {
            "id": "p004", "title": "P04 结论先行", "chapter": "为什么",
            "kind": "content", "outline": ["先跑通", "再优化"], "code": "",
        }
        html = builtin_ppt.build(page, None)
        self.assertRegex(html, r"<h1[^>]*>结论先行</h1>")
        self.assertNotIn("<h1>P04", html)
        self.assertIn("window.innerWidth / 1280", html)

    def test_index_links_are_basenames(self):
        out = Path(tempfile.mkdtemp())
        pages = [{"id": "p001", "title": "封面", "html": r"out\3_htmlppt\p001.html"}]
        index = ppt.write_index(pages, out, "测试")
        text = index.read_text(encoding="utf-8")
        self.assertIn('href="p001.html"', text)
        self.assertNotIn("out\\3_htmlppt", text)

    def test_svg_wrapper_is_self_contained(self):
        out = Path(tempfile.mkdtemp())
        svg = out / "p001.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">'
                       '<rect width="10" height="10"/></svg>', encoding="utf-8")
        html = ppt.build_page_from_svg(
            {"id": "p001", "title": "封面"}, 0, out, out, out, pipeline.Log(out),
        )
        text = (out / html).read_text(encoding="utf-8")
        self.assertNotIn("file://", text)
        self.assertIn("<svg", text)


if __name__ == "__main__":
    unittest.main()
