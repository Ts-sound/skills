---
deck_id: solarized-episode
kind: deck
category: general
summary: 节目式深度测评与知识分享，按章节推进；Solarized Light 米色纸感、深色胶囊波形与底部按章节顺序填充的 chip 进度带，适合播客式讲解、产品测评与长文拆解，共 16 页。
keywords: [测评, 播客, 节目, 章节进度, solarized, 技术分享, 16页]
primary_color: "#268BD2"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
replication_mode: standard
native_structure_mode: structured
page_count: 16
---

# Solarized Episode — Design Specification

## I. Template Overview

| Application context | Definition |
| --- | --- |
| Recurring presentation family | 节目式深度测评、产品拆解、播客配套图文与知识分享，按章节分段推进，一期 16 页 |
| Intended audiences and outcomes | 面向读者与听众；让受众在一页内抓住一个论点，并清楚自己处在整期的第几段 |
| Delivery and reading assumptions | 以屏幕分享与录屏讲解为主，也需要单独流转阅读；底部 chip 进度带承担“位置感”，不能依赖口头补充 |
| Representative narrative/page roles | 封面、目录、章节（7）、开放正文（2）、三卡论点（2）、数据条（2）、收尾（1）；总计 16 页 |
| Roster shape | 7 个 Layout、16 个页面：章节页与内容页复用同一套 Layout，只换文案与 chip 状态 |

- 视觉基调是 Solarized Light 的米色纸感：底 `#FDF6E3`，标题深墨 `#073642`，正文暖灰 `#657B83`，强调用橙 `#CB4B16`，数据用蓝、黄、青分区。
- 结构上只有一个 Master（`Solarized Episode`），七个 Layout 按页面职责分工；不按单页拆 Master。
- 每页底部固定一条“位置带”：七枚章节 chip 按顺序从左往右填充 + 右端页码 `Pnn / 16`；已走过的章节填实，当前章节橙色，未到的保持浅底。

## II. Color Scheme

| Role | Color | Application |
| --- | --- | --- |
| Paper | #FDF6E3 | Master 背景与页面底色 |
| Paper wash | #FFFCF3 | 顶部 300px 渐变亮区，模拟纸面受光 |
| Panel | #EEE8D5 | 卡片与结论面板底 |
| Ink | #073642 | 标题、深色胶囊、关键结论 |
| Body | #657B83 | 正文与说明文字 |
| Muted | #93A1A1 | 页码、来源、次要标签 |
| Meta | #586E75 | 页脚与已完成 chip 底色 |
| Accent orange | #CB4B16 | 强调短杠、当前章节 chip、编号 |
| Data blue | #268BD2 | 主色：指标 1 与结构类强调 |
| Data yellow | #B58900 | 指标 2 与英文小标 |
| Data teal | #2AA198 | 指标 4 |
| Rule | #E7DCC1 | 分隔线、卡片描边 |
| Chip done | #586E75 | 已走过章节的 chip 底色 |
| Chip active | #CB4B16 | 当前章节 chip 底色 |
| Chip idle | #F0E8D4 | 未到章节的 chip 底色 |
| Chip text on dark | #FDF6E3 | 已完成 / 当前 chip 的文字 |
| Chip idle text | #93A1A1 | 未到章节的文字 |

## III. Typography

| Role | Font stack | Application |
| --- | --- | --- |
| Display | `Noto Serif SC, Source Han Serif SC, serif` | 封面主标题、页面标题、章节标题、卡片标题、收尾语 |
| Body | `Noto Sans SC, Source Han Sans SC, Arial, sans-serif` | 正文、目录行、卡片说明、页脚、chip 标签 |
| Data | `Noto Sans SC, Arial, sans-serif` | 指标数字、页码、章节号 |

- 标题用衬线（Noto Serif）制造“印刷物”气质，正文用无衬线（Noto Sans）保证屏读清晰。
- 两族均为 SIL Open Font License 1.1，可商用、可嵌入导出；不使用 SimSun / 微软雅黑等系统内嵌商业字库，避免商用授权风险。
- 随模板附带 `fonts/NotoSerifSC-VF.ttf` 与 `fonts/NotoSansSC-VF.ttf`（OFL 1.1），安装后即为所见即所得；未装时字体栈会落到 `Source Han *` 与泛型 `serif` / `sans-serif`，版面不塌。
- 字号阶梯：封面标题 46 / 章节标题 44 / 页面标题 38 / 卡片标题 21 / 目录 20 / 正文 17–18 / 说明 14 / 标签 11–13 / 章节号 132。

## IV. Signature Design Elements

- 左上角 56×4 的橙色短杠是每页的“开篇记号”，标题永远从短杠下方起排。
- 封面中部一枚 600×92 的深墨胶囊波形条，是全套唯一的图形化装饰；由 33 根等宽细柱组成，中间高两端低的对称包络。
- 底部章节带：七枚等高胶囊 chip 铺满 80–1096，等距 8px，按章节名长度（`len+6` 权重）分配宽度；三态——已完成 `#586E75` 实底反白、当前 `#CB4B16` 实底反白加粗、未到 `#F0E8D4` 底 + `#93A1A1` 字。页码 `Pnn / 16` 右端对齐（Noto Sans SC 12，`#93A1A1`）。
- 进度是顺序的：第 n 页只点亮前 n 个章节中的已完成项与当前项，绝不跳序或全亮；封面与目录页保持全浅底（还没进入任何章节）。
- chip 行是页面内容而不是 Layout 固定件：同一行复制到每页，只改三态配色；章节增删时按同一套宽度算法重排。
- 卡片一律 16px 圆角、`#EEE8D5` 底、`#E7DCC1` 细描边，顶部 48×3 彩色短规标识分类。
- 数据条用四色细规分区，指标数字 46px，标签 13px 置于数字下方 34px。

## V. Page Roster

| File | Master | Layout key | PowerPoint picker name | Visual character | Reusable slots |
| --- | --- | --- | --- | --- | --- |
| `01_cover.svg` | Solarized Episode | cover | Cover — Episode Opener | 居中 kicker、双行衬线标题、深墨波形胶囊 | 栏目标（body）、标题、副标题、日期、署名（body）、章节 chip 行、页码 |
| `02_toc.svg` | Solarized Episode | agenda | Agenda — Episode Map | 橙色短杠 + 七行编号目录 + 底部规则线 | 小标（body）、标题、目录列表（body）、章节 chip 行、页码 |
| `03_section.svg` | Solarized Episode | section | Chapter Opener | 132px 浅色章节号、衬线大标题、一句导语 | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `04_content.svg` | Solarized Episode | content | Title and Content | 短杠 + 标题 + 全宽自由正文区 | 标题、正文（body）、章节 chip 行、页码 |
| `05_section.svg` | Solarized Episode | section | Chapter Opener | 同上（第二章开场），复用 section Layout | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `06_content_cards.svg` | Solarized Episode | content-cards | Three Arguments | 三等分圆角卡片，顶部彩色短规，卡片下方一行结论 | 标题、三张卡片（object×3）、结论（body）、章节 chip 行、页码 |
| `07_section.svg` | Solarized Episode | section | Chapter Opener | 同上（第三章开场） | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `08_content_data.svg` | Solarized Episode | content-data | Metric Strip | 四格指标 + 底部结论面板 | 标题、四个指标（object×4）、结论（body）、章节 chip 行、页码 |
| `09_section.svg` | Solarized Episode | section | Chapter Opener | 同上（第四章开场） | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `10_content_data.svg` | Solarized Episode | content-data | Metric Strip | 四格指标（成本口径）+ 结论面板 | 标题、四个指标（object×4）、结论（body）、章节 chip 行、页码 |
| `11_section.svg` | Solarized Episode | section | Chapter Opener | 同上（第五章开场） | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `12_content_cards.svg` | Solarized Episode | content-cards | Three Arguments | 三卡（五层栈的三段） | 标题、三张卡片（object×3）、结论（body）、章节 chip 行、页码 |
| `13_section.svg` | Solarized Episode | section | Chapter Opener | 同上（第六章开场） | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `14_content.svg` | Solarized Episode | content | Title and Content | 三条行动 + 衡量标准的正文页 | 标题、正文（body）、章节 chip 行、页码 |
| `15_section.svg` | Solarized Episode | section | Chapter Opener | 同上（第七章开场） | 章节号（body）、标题、导语（body）、章节 chip 行、页码 |
| `16_ending.svg` | Solarized Episode | closing | Closing | 居中收尾语、橙色短线、版权行 | 收尾语、联系信息（subtitle）、版权（body）、章节 chip 行、页码 |

- 章节顺序：开场判断 / 不是工具清单 / 超级个体机制 / 本期生产链路 / 五层能力栈 / 老板与个体行动 / 收束与评论。
- 页码与 `page_count: 16` 一一对应（P01–P16）；七枚 chip 的文案与顺序是本模板的示例章节，实际项目按本期目录替换，保持宽度算法与三态配色即可。
- 页码为空槽意义上的 `slide-number` 占位符；底部没有单独的章节名文本槽，章节位置由 chip 行表达。

## VI. Assets

- 位图与导入矢量：无。全部版式由形状、文字与渐变构成，换主题色只需改 `#CB4B16` 与四个数据色。
- 字体文件：`fonts/NotoSerifSC-VF.ttf`（标题）、`fonts/NotoSansSC-VF.ttf`（正文），SIL OFL 1.1，允许随模板分发；安装后重新打开 PPTX 即可正确回退。
