# PPTX 创建、编辑与分析

> 脚本路径均相对本 skill 根目录（如 `scripts/office/validate.py`）。
> **Windows + Office 环境适配（工具缺失时）**：
> - `markitdown`、`soffice`、`pdftoppm` 缺失时：**读取内容**按 SKILL.md『读取路线怎么选』决策——markitdown 在则优先，不在走 `scripts/extract_office_text.ps1`（COM，逐页文本 + 备注）；`.potx` 先复制成 `.pptx` 再喂给它。
> - `pptxgenjs` 多数环境**未预装**：在输出目录 `npm install pptxgenjs` 再 `require('pptxgenjs')`。
> - `thumbnail.py` 依赖 soffice 渲染，无 LibreOffice 时不可用 — 选模板版式可改为用 PowerPoint COM 导出每页图片（`Export` 方法）。
> - `add_slide.py` / `clean.py` / `office/validate.py` 纯 Python（需 `pip install defusedxml lxml Pillow`），可直接用。

`.pptx` 是 ZIP 打包的 XML 文件集合。按任务选路线：

| 任务 | 路线 |
|---|---|
| **新建** deck | 写 `pptxgenjs` 脚本 — 见下方坑点 |
| **编辑**现有 deck，或从模板构建 | unzip → 改 `ppt/slides/slideN.xml` → zip |
| **读取**内容 | `markitdown deck.pptx`（在则优先——每页一块，带 `<!-- Slide number: N -->` 标记）；不在 → `scripts/extract_office_text.ps1`（COM，逐页文本 + 备注）。视觉网格：`python scripts/thumbnail.py deck.pptx`（需 soffice）。决策规则见 SKILL.md"读取路线怎么选" |

## 脚本

| 脚本 | 作用 |
|---|---|
| `scripts/thumbnail.py deck.pptx [prefix]` | 每页带标签的缩略图网格，用于挑模板版式。仅 `.pptx`。务必传 prefix — 默认 `thumbnails` 会覆盖同目录其他 deck 的网格 |
| `scripts/add_slide.py unpacked/ slide2.xml [--after slideN.xml]` | 复制一页（或一个 `slideLayoutN.xml`）并做完所有包登记。也接受 `.pptx` 直连 + `-o out.pptx` |
| `scripts/clean.py unpacked/` | 删除不再被引用的页、媒体、rels。在 `<p:sldIdLst>` 定稿**之后**运行 |
| `scripts/office/validate.py deck.pptx [--original src.pptx]` | schema、关系、content-type、图表和页检查；每个失败都给出修法。模板派生的 deck 务必传 `--original` 做基线 |
| `scripts/office/soffice.py --headless --convert-to pdf deck.pptx` | LibreOffice 包装（无 soffice 时改用 PowerPoint COM `SaveAs`/`ExportAsFixedFormat`） |

## 用 pptxgenjs 创建 — 坑点

- **加页前先设 `pres.layout`。** 默认画布 `LAYOUT_16x9` = **10″ × 5.625″**，不是 13.3″ 宽。越界坐标会被原样写入，不做钳制 — 形状就是不在页上。（`LAYOUT_WIDE` 是 13.3″ × 7.5″。）
- **十六进制颜色：绝不带 `#`，绝不用 8 位。** `color: "FF0000"`。`"#FF0000"` 和把 alpha 掺进 hex（`"00000020"`）都会**损坏文件**。半透明：填充和图片用 `transparency: 0-100`，阴影用 `opacity: 0.0-1.0` — 用在对方身上会被静默忽略。
- **pptxgenjs 原地修改传入的 option 对象**（首次使用即转 EMU）。绝不跨两次 `add*` 调用共享一个 `shadow`/options 对象 — 每次新建。
- **阴影 `offset` 必须 ≥ 0** — 负偏移损坏文件。想往上投影，用 `angle: 270` 配正偏移。
- **`letterSpacing` 被静默忽略** — 真正的选项是 `charSpacing`。
- **列表：** 每项 `bullet: true`，绝不手写 `•`（渲染出双 bullet）。数组项除最后一项外每项设 `breakLine: true`。bulleted 段落间距用 `paraSpaceAfter`，不用 `lineSpacing`（巨大空隙）。
- **每个输出文件一个 `new pptxgen()`** — 绝不复用实例。
- **`rectRadius` 只对 `ROUNDED_RECTANGLE` 有效**，对 `RECTANGLE` 无效。
- **不支持渐变填充** — 用渐变图片做背景。
- **文本框有内置内边距** — 文本要与同 x 的形状/线条/图标对齐时设 `margin: 0`。
- **演讲者备注走 `slide.addNotes("...")`**（纯文本，每页一次），不要放页上文本框里。
- **图表保持原生。** PowerPoint 能画的都用 `addChart()`（组合图传 `{type, data, options}` 数组）。库里没有的 PowerPoint 原生特性（趋势线、误差线），自己算出附加系列或后处理生成的 OOXML — 不要退回渲染图片。只有 PowerPoint 无原生形态的（桑基、网络、弦图）才进图片。
- **默认图表裸渲染** — 无标题、无数据标签、老气配色。设 `showTitle` + `title`、`showValue: true` + `dataLabelPosition`、`chartColors: [...]`、并把边框安静下来（`catAxisLabelColor`/`valAxisLabelColor`、`valGridLine: { color, size }`、`catGridLine: { style: "none" }`、单系列 `showLegend: false`）。
- **堆叠柱/条图 `dataLabelPosition` 只能 `ctr`、`inEnd`、`inBase`。** `outEnd` **损坏文件**。
- **组合图系列用 `secondaryValAxis`/`secondaryCatAxis` 时，图表选项必须同时有 `valAxes` 和 `catAxes`，各两个条目。** 否则 pptxgenjs 写出从未声明的坐标轴 *id*，PowerPoint **丢弃整个图表**并报文件损坏。只给 `valAxes` 不够。
- **`writeFile()` 之后，跑 `python scripts/office/validate.py deck.pptx`。** 它报告上面两个图表故障和 PowerPoint 拒绝的页 XML 缺陷，并逐个给出修法。在生成器里修，不要手改打包后的 XML。
- **绝不重排 `<p:presentation>` 的子元素。** pptxgenjs 把 `<p:notesMasterIdLst>` 写在 `<p:sldIdLst>` 后面并让两个 master 指向同一 theme。PowerPoint 读得正常 — 挪了同一份 deck 就打不开了。
- **图标：** `react-icons` 渲染成 SVG（`ReactDOMServer.renderToStaticMarkup`），用 `sharp` 以 ≥256px 栅格化，经 `addImage({ data: "image/png;base64," + buf.toString("base64") })` 插入 — `image/png;base64,` 前缀必需（未预装的环境 `npm install react-icons react react-dom sharp`）。

## 编辑现有 deck 和模板

先选版式：`python scripts/thumbnail.py template.pptx template-thumbs`（需 soffice，缺失时的替代见顶部环境适配）。配合内容 dump 把每个章节映射到模板页，并变换版式 — 不要把所有章节都塞进同一种标题+bullet 页。

```bash
python -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall('unpacked')" deck.pptx
python scripts/add_slide.py unpacked/ slide2.xml --after slide2.xml   # 复制一页（或 slideLayoutN.xml）；打印新页路径
# 重排 / 删页 = 改 ppt/presentation.xml 里的 <p:sldIdLst>
python scripts/clean.py unpacked/                                     # 删除后清孤儿：页、媒体、rels
# 在 ppt/slides/slideN.xml 里改页内容
(cd unpacked && rm -f ../out.pptx && zip -Xr ../out.pptx .)           # 在目录内部 zip；先 rm 否则已删部件会复活
python scripts/office/validate.py out.pptx --original deck.pptx
```

- **所有结构性操作 — 增、删、重排 — 都在改任何页内容之前做完。** `add_slide.py` 逐字复制页文件，编辑之后再复制会克隆已编辑内容；`clean.py` 会删掉 `<p:sldIdLst>` 里没有的任何页，包括你刚写好的。
- **绝不手复制页文件** — `add_slide.py` 做新页需要的全部登记并报告产物（`Created ppt/slides/slide17.xml from slide2.xml`）。它也能直连文件：`add_slide.py deck.pptx slide2.xml -o out.pptx` — **传 `-o`，否则原地重写输入 deck。** 复制出的页仍*引用*源页的图表/SmartArt/嵌入对象部件而非克隆，改一页的图表另一页跟着变。
- **用 `python-pptx` 的话**，三件它做不到的事：复制页（唯一入口是 `add_slide(layout)`）、经 `text_frame.text = "..."` 保留格式（会把段落塌缩成单个无样式 run — 改赋 `run.text`）、读取模板美术常用的 SVG/EMF（`add_picture` 抛 `UnidentifiedImageError`）。
- 老格式 `.ppt` 必须先转换（Windows + Office：PowerPoint COM `Presentations.Open` 后 `SaveAs` ppSaveAsPPTX=24；有 LibreOffice 的环境：`python scripts/office/soffice.py --headless --convert-to pptx file.ppt`）。`.potx` 模板解压打包方式相同 — 输出保留 `.potx` 扩展名。
- 要复用模板里的图标或图片，复制一个本来就含它的页或版式。

往模板里填内容时：

- 脚本化 XML 变换时，用 `defusedxml.minidom` 解析 — OOXML 经 `xml.etree.ElementTree` 往返会重写命名空间前缀并损坏 deck。
- **模板槽位 ≠ 源条目。** 模板有 4 个成员而你有 3 个时，删除第 4 个成员的整个 group（图片 + 文本框），不只是文本 — 之后 QA 检查孤儿视觉元素。
- 每个列表项一个 `<a:p>` — 绝不把多项拼进一个段落。复制相邻 `<a:pPr>` 保住间距，标题、节头、行内标签（`Status:`、`Owner:`）的 `<a:rPr>` 上放 `b="1"`。
- 让 bullet 从版式继承；只有要覆盖时才加 `<a:buChar>`、`<a:buAutoNum>`（编号）或 `<a:buNone>` — 绝不在文本里手写 `•`。
- 前后带空格的文本，其 `<a:t>` 需要 `xml:space="preserve"`。

## 设计思路

**别做无聊的页。** 白底纯 bullet 不会打动任何人。每页从下面的清单里找灵感。

### 动手之前

- **选一套大胆、贴内容的配色**：配色要为*这个*主题而设计。把你的颜色换到另一个完全不同的演示里还能"用"，说明选得不够具体。
- **主次分明**：一个颜色主导（60-70% 视觉权重），1-2 个辅助色调 + 一个锐利强调色。绝不平均分配所有颜色。
- **深浅对比**：标题页 + 结论页深色，内容页浅色（"三明治"结构）。或者全程深色走高级感。
- **定一个视觉母题（motif）**：挑一个有辨识度的元素并贯穿 — 圆角图片框、彩色圆圈里的图标。**不要用色条或强调条纹当母题**（见 Avoid）。

### 配色

选贴合主题的颜色 — 别默认烂大街的蓝。可作起点：

| 主题 | 主色 | 辅色 | 强调色 |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (藏青) | `CADCFC` (冰蓝) | `FFFFFF` (白) |
| **Forest & Moss** | `2C5F2D` (森林) | `97BC62` (苔藓) | `F5F5F5` (奶油) |
| **Coral Energy** | `F96167` (珊瑚) | `F9E795` (金) | `2F3C7E` (藏青) |
| **Warm Terracotta** | `B85042` (陶土) | `E7E8D1` (沙) | `A7BEAE` (鼠尾草) |
| **Ocean Gradient** | `065A82` (深蓝) | `1C7293` (青) | `21295C` (午夜) |
| **Charcoal Minimal** | `36454F` (炭灰) | `F2F2F2` (灰白) | `212121` (黑) |
| **Teal Trust** | `028090` (青) | `00A896` (海泡) | `02C39A` (薄荷) |
| **Berry & Cream** | `6D2E46` (浆果) | `A26769` (灰玫瑰) | `ECE2D0` (奶油) |
| **Sage Calm** | `84B59F` (鼠尾草) | `69A297` (桉树) | `50808E` (石板) |
| **Cherry Bold** | `990011` (樱桃) | `FCF6F5` (灰白) | `2F3C7E` (藏青) |

### 每一页

**每页都要有视觉元素** — 图片、图表、图标或形状。纯文本页没有记忆点。

**版式选项：**
- 双栏（左文右图）
- 图标 + 文字行（彩色圆圈里的图标，加粗标题，下方描述）
- 2×2 或 2×3 网格（一侧大图，另一侧内容块网格）
- 半出血图片（整左或整右侧）+ 内容叠加

**数据展示：**
- 大数字统计（60-72pt 大数字，下方小标签）
- 对比栏（前后、利弊、并排选项）
- 时间线或流程（编号步骤、箭头）

**视觉打磨：**
- 节标题旁彩色小圆圈里的图标
- 关键统计或标语用斜体强调

### 字体

**写进 .pptx 的字体名由用户的 PowerPoint 渲染，不是本环境。** 视觉 QA 经 LibreOffice 渲染，它会替换没有的字体 — 有些字体的替身宽度不同，QA 预览可能显示真实 deck 不会有的溢出（或反之）。保持 QA 可信：

- **安全字体**（QA 宽度保真 *且* 随 Office 分发）：**Arial, Calibri, Cambria, Times New Roman, Courier New, Bookman Old Style, Century Schoolbook**。正文和一切讲究排版的地方用这些。
- **零 QA 风险的个性标题**：安全清单里的衬线标题（Cambria、Bookman Old Style、Century Schoolbook）配安全清单无衬线正文（Calibri 或 Arial）。
- **用户点名安全清单外的字体**（如 Georgia、Trebuchet MS）：用户要求处照用，但容器多留 ~10% 余量，别信这些元素的 QA 文本适配 — 预览是近似的。用户没指定时正文优先安全清单。
- **QA 不可靠字体**（替身宽度不同 — 溢出检查可能错）：Georgia, Trebuchet MS, Impact, Arial Black, Garamond, Consolas, Palatino Linotype。Calibri Light 替身因环境而异，按不可靠处理。做标题/强调留余量可以；别信这些的 QA 适配。
- **绝不默认 Aptos** — Office 2023 后的默认字体，本环境无度量兼容替身 *且* 老版 Office 没装，两头都不可靠。

| 元素 | 字号 |
|---------|------|
| 页标题 | 36-44pt 粗体 |
| 节标题 | 20-24pt 粗体 |
| 正文 | 14-16pt |
| 说明文字 | 10-12pt 弱化 |

### 间距

- 最小边距 0.5″
- 内容块间 0.3-0.5″
- 留呼吸空间 — 别填满每一寸

### 避免（常见错误）

- **别重复同一版式** — 各页变换栏、卡片、callout
- **别居中正文** — 段落和列表左对齐；只有标题居中
- **别吝啬字号对比** — 标题要 36pt+ 才能从 14-16pt 正文里跳出来
- **别默认蓝色** — 选贴合具体主题的颜色
- **别随机混间距** — 选定 0.3″ 或 0.5″ 间距并保持一致
- **别只美化一页其余摆烂** — 要么全情投入要么全程朴素
- **别做纯文本页** — 加图片、图标、图表、视觉元素；避免裸标题 + bullet
- **别忘了文本框内边距** — 线条或形状与文本边缘对齐时，文本框设 `margin: 0` 或为内边距偏移形状
- **别用低对比元素** — 图标*和*文本都要与背景强对比；避免浅底浅字、深底深字
- **绝不在标题下加强调线** — AI 生成页的标志；用留白或背景色代替
- **绝不加装饰色条或强调条纹** — 包括：横跨页宽的页眉/页脚条、沿一侧边的竖向边条、卡片或内容块一侧的细强调条、矩形的"单边框"。这些读作 AI 填充物。想让卡片突出，用轻底色、投影或图标 — 不要边条。
- **别默认奶油/米色背景** — 没指定背景时用白（`FFFFFF`）或用户品牌色；避免 `F5F5DC`、`FAF0E6`、`FAEBD7`、`FFF8E1` 等暖中性默认
- **别交付溢出形状的文本** — 放不下就缩字号、拆页或加大容器；绝不留内容被截断或溢出边界

## QA（必做）

第一版渲染通常有几个真问题 — 重叠、溢出、错位。找出来修掉，只重渲染改过的页，然后收手。

### 内容 QA

markitdown 可用则 `markitdown output.pptx`，否则重跑 `scripts/extract_office_text.ps1` 对输出 deck 提取文本核对。

查缺失内容、错别字、错序。**用模板时查残留占位文本：**

```bash
markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout"
```

（无 markitdown 时用提取出的 txt 做同样的 grep。）有结果就在宣布完成前修掉。

### 文件 QA（必做）

```bash
python scripts/office/validate.py output.pptx                      # 从零构建
python scripts/office/validate.py output.pptx --original src.pptx  # 从模板构建
```

**模板派生的 deck 永远传 `--original`。** 模板本身可能就有 XSD 拒绝的部件，裸跑会报你从未造成的失败 — 真回归可能藏在其中。`--original` 把 schema 和页检查对模板做基线，抑制它已有的错误。结构性检查 — 关系、content type、图表 — 不理会 `--original`，照报模板继承的问题，按其本身是非来判断。

pptxgenjs 会生成 PowerPoint 拒绝打开、而其他工具都接受的图表 XML：python-pptx 打得开、LibreOffice 渲染得出、XSD 也过。每个失败都给出修法。在生成器里修并重建。

### 视觉 QA

把页转成图片（PowerPoint COM 导出，或装 LibreOffice + Poppler 后走下方流程）逐页检查。盯着生成代码看久了会看见预期而非实际渲染，要看就看新鲜的图（有 subagent 的话交给它效果好）。要找的用户可见缺陷：

- **文本溢出或在框/页边界被截断 — 首先查这个。** 最高频缺陷且永远用户可见。（字体预览不可靠时，预览是近似的：信你留的 ~10% 余量，不是表观的适配。）
- 元素重叠（文字压形状、线条穿字、元素堆叠）
- 来源引用或页脚与上方内容相撞
- 元素太近（< 0.3″ 间隙）或卡片/区块几乎贴上
- 间距不匀（一处大片空白另一处拥挤）
- 距页边距不足（< 0.5″）
- 栏或相似元素对齐不一致
- 低对比文本（如灰白底上的浅灰字）
- 文本替换后模板装饰错位 — 如标题下划线按一行定位，替换后的标题折成了两行
- 低对比图标（如深底上的深色图标没有对比色圆圈）
- 文本框过窄导致过度折行
- 残留占位内容

## 转图片（LibreOffice + Poppler 流程）

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**把上面打印的绝对路径直接交给 view 工具。** `rm` 清掉上次的旧图。`pdftoppm` 按总页数零填充：10 页内 `slide-1.jpg`，10-99 页 `slide-01.jpg`，100+ 页 `slide-001.jpg`。

**修复后重跑全部四条命令** — PDF 必须从编辑后的 `.pptx` 重新生成，`pdftoppm` 才能反映你的修改。

无 LibreOffice/Poppler 时的替代（PowerPoint COM，PowerShell）：

```powershell
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open("D:\path\deck.pptx", $true, $false, $false)  # ReadOnly
$pres.Export("D:\path\slide_imgs", "JPG", 1500, 844)   # 导出整目录 JPG
$pres.Close(); $pp.Quit()
```

## 依赖

`pptxgenjs` (npm) · `markitdown[pptx]`, `Pillow`, `defusedxml`, `lxml` (pip) · LibreOffice (`soffice`) · `pdftoppm` (Poppler)
环境要求：Node（`npm install pptxgenjs`）· Python（`pip install Pillow defusedxml lxml`）· markitdown（pip 可装）· LibreOffice/Poppler 缺失时按上文替代方案走。
