---
name: awesome-seedance
description: "Seedance 2.0 提示词与玩法库 — 收录 40+ 条高保真、可直接复制的 Seedance 2.0 视频提示词，按 7 大题材分类：电影级风格（好莱坞赛车 / 维伦纽瓦沙漠史诗 / 王家卫雨夜）、广告与品牌、社媒爆款梗、UGC 纪实、动漫动画、短剧网剧（含中式竖屏短剧 / 豪门恩怨）、视觉特效实验。另含 9 大商用玩法中文案例。触发词：Seedance、即梦、豆包视频、Seedance 2.0 提示词、seedance prompt。"
license: MIT
source: https://github.com/ZeroLu/awesome-seedance
---

# Awesome Seedance 2.0 提示词库

从 X（Twitter）、微信公众号、一线提示词工程师处甄选的高保真 Seedance 2.0 提示词合集。全部为**可直接复制粘贴**的完整分镜提示词。

## 用法

1. 按题材从下表选参考 → 读 `references/prompt-collection-en.md`（英文）或 `prompt-collection-zh.md`（中文）对应小节。
2. 复制该条提示词的**结构**（时长 + 分镜时间码 + 逐镜画面 + 对白/字幕提示），替换成你自己的主体与场景。
3. Seedance 提示词通用结构（本库所有条目都遵循）：
   - `Style:` 风格关键词（可加导演/影调描述）
   - `Duration:` 时长
   - `[00-05s] Shot 1: 景别 + 画面内容 + 对白/字幕提示`
   - `[05-10s] Shot 2: ...` / `[10-15s] Shot 3: ...`
4. 中文商用玩法见 `references/commercial-use-cases-zh.md`（卡尔的 AI 沃茨总结的九大商用场景）。

## 内容地图

**`references/prompt-collection-en.md`（英文，40+ 条）**

| 小节 | 内容 |
|---|---|
| 1. Cinematic Film Styles | 好莱坞赛车（勒芒雨夜）、维伦纽瓦沙漠史诗（IMAX 70mm）、王家卫雨夜电话亭、大片提示词包、时间码电影序列、爵士钢琴原生音画同步 |
| 2. Advertising & Commercial Branding | 无印良品品牌片、香水 MG 动画、时间码香水广告 |
| 3. Social Media & Viral Memes | 巨型橘猫梗、酸面包椒盐卷街头吵架 |
| 4. UGC Style | 超现实纪实、室内参考角色 + 音频 |
| 5. Anime & Animation Styles | 武术擂台、哪吒敖丙冰火对决（时空折叠）、水獭机甲战、10 种动画风格、动态图形、梵高后印象派动画、动漫角色武道大会、路飞敲代码 |
| 6. Short-form Drama & Web Series | 春晚甄嬛传风格、中式微短剧雨夜情感戏、中式竖屏霸总短剧 |
| 7. Visual Effects & Experimental | 超现实巨物恐惧、参考照片间的流体变形、轨道碰撞物理、图生视频物理动画 |
| 8. Resources | API 与使用教程 |

**`references/prompt-collection-zh.md`（中文，同样内容的对应译本）**

**`references/commercial-use-cases-zh.md`（中文，9 大商用玩法）**
追热点（飞驰人生同款）、商业广告（运动饮料）、品牌宣传（无印良品）、穿搭变装、直播带货（口播 + 字幕）、动态海报（九宫格分镜）、广告复刻（无人机）、真人短剧（豪门恩怨）、AI 漫剧（武侠）。

## 使用要点（提炼自本库）

- **分镜时间码是核心**：Seedance 对 `[00-05s]` 这类时间切片理解很好，尽量逐段写清"画面 + 对白 + 字幕"。
- **产品一致性**：广告类提示词中明确"在所有分镜中保持产品一致性"，Seedance 能做到。
- **九宫格分镜把控不精准** → 在提示语中补写元素出现顺序。
- **参考驱动**：给一段参考视频/图片，Seedance 能对齐风格（`模仿 @视频1 的分镜设计，把产品替换成 @图片1...`）。
- **IP 名称**：Seedance 2.0 的 IP 过滤较激进，避免直接写知名 IP 名。
- **痛点**：排队久（高峰期 2 小时起步），凌晨较通畅。

## 声明

- 本库为第三方社区合集，原作者署名与来源链接保留在文件内（`*Source: ...*`）；部分条目含赞助商链接，仅为原仓库内容，与本技能功能无关。
- 提示词版权归原作者，采用 MIT 许可分发。
