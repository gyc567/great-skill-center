# DOCX 创建、编辑与分析

> 脚本路径均相对本 skill 根目录（如 `scripts/office/validate.py`）。
> **Windows + Office 环境适配（工具缺失时）**：
> - `pandoc`、`soffice.py` 渲染验证、`pdftoppm` 缺失时：读取按 SKILL.md『读取路线怎么选』决策（pandoc 在则优先，不在走 `scripts/extract_office_text.ps1` COM 提取）；渲染验证改用 Word COM。
> - **渲染验证**：Word COM 的 `ExportAsFixedFormat` 转 PDF，或装 LibreOffice + Poppler 后按官方流程走。
> - `docx` (npm) 多数环境**未预装**：先在项目目录 `npm install docx`，再 `require('docx')`。
> - `scripts/office/validate.py` 只需 Python + `defusedxml`（`pip install defusedxml`），不依赖 LibreOffice，可直接用。

`.docx` 是 ZIP 打包的 XML 文件集合。按任务选路线：

| 任务 | 路线 |
|---|---|
| **新建**文档 | 写 `docx` (npm) 脚本 — 见下方坑点 |
| **编辑**现有文档 | `unzip` → 改 `word/document.xml` → `zip`（docx-js 打不开已有文件） |
| **读取**内容 | `pandoc -t markdown file.docx`（pandoc 在则优先——带结构 markdown，质量最高）；不在或带保护壳 → `scripts/extract_office_text.ps1`（COM，支持 .doc/.docx/.rtf，含表格）。决策规则见 SKILL.md"读取路线怎么选" |

## 用 docx-js 创建 — 坑点

`docx` 库模型已知 API，以下是实际会踩的坑（未预装的环境先 `npm install docx`）：

- **页面默认 A4。** US Letter 需 `page: { size: { width: 12240, height: 15840 } }`（DXA；1440 = 1″）。
- **横向：** 传纵向尺寸 + `orientation: PageOrientation.LANDSCAPE` — docx-js 内部自行交换宽高。
- **表格需要双宽度：** 表级设 `columnWidths` 且每个 cell 设 `width`，都用 `WidthType.DXA`（PERCENTAGE 在 Google Docs 里会坏）。列宽之和必须等于表宽。
- **表格底纹：** 用 `ShadingType.CLEAR`，绝不用 `SOLID`（渲染成黑色）。
- **列表：** 绝不手写 `•`；用带 `LevelFormat.BULLET` 的 `numbering` 配置。
- **`ImageRun` 必须带 `type:`**（`"png"`、`"jpg"` …）。
- **`PageBreak` 必须包在 `Paragraph` 里。**
- **绝不用 `\n`** — 用独立的 `Paragraph` 元素。
- **TOC：** 标题必须用内置 `HeadingLevel.*`；自定义标题样式需设 `outlineLevel`，否则不进目录。
- **不要用表格做水平分隔线** — 用段落底边框。
- **点线引导符 / 同行右对齐：** 在 `TextRun` 内用 `PositionalTab`（`alignment: PositionalTabAlignment.RIGHT`, `leader: PositionalTabLeader.DOT`），不要手写 `.` 或空格填充。

## 验证输出

写完 `.docx` 后渲染出来亲眼检查。官方流程（需 LibreOffice + Poppler）：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 100 output.pdf page
ls page-*.jpg   # 然后 Read 这些图片
```

无 LibreOffice 时的替代：Word COM 导出 PDF 后再转图，或让用户在 Word 里打开确认。

`pdftoppm` 对页号做零填充，宽度取决于总页数（`page-01.jpg`…`page-12.jpg`）。

## 编辑现有文档

老格式 `.doc` 必须先转换：Windows + Office 用 Word COM（`Documents.Open` 后 `SaveAs2` FileFormat=12 即 wdFormatXMLDocument）；有 LibreOffice 的环境用 `python scripts/office/soffice.py --headless --convert-to docx file.doc`。

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete   # 删除符号链接条目 — 外部来源的 docx 不可信
python scripts/merge_runs.py unpacked/   # 合并碎片 run，让文本可查找
# 直接改 unpacked/word/document.xml — 不要重排版/美化打印
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python scripts/office/validate.py out.docx --original doc.docx   # XSD 校验；--auto-repair 修常见问题
# 修订模式？加 --author "<你署名的作者名>" 检查每处编辑是否被跟踪
```

Word 会把文本拆进很多 `<w:r>` run（修订 id、拼写检查标记），所以文档里肉眼可见的短语在 XML 里往往不是连续字符串。`merge_runs.py` 合并 `word/document.xml` 中相邻同格式 run，不改内容不改渲染；也接受 `.docx` 直接输入（`python scripts/merge_runs.py doc.docx -o merged.docx`）。

**修订（tracked changes）：** 修订模式下校验必须加 `--author "<你署名的作者名>"`（需 `--original`）— 它报告任何没被 `<w:ins>`/`<w:del>` 包住的改动，这种失误极易发生且接受修订后不可见。把 run 包进带 `w:id`、`w:author`、`w:date` 属性的 `<w:ins>`/`<w:del>`。`<w:del>` 内的文本元素是 `<w:delText>`，不是 `<w:t>`。删除段落标记（`<w:pPr><w:rPr><w:del w:id=".." w:author=".." w:date=".."/></w:rPr></w:pPr>`）意思是"本段并入下一段"— 所以整段删除 = 这个标记 + 每个 run 外包 `<w:del>`。`<w:del/>` 必须在 rPr 其他子元素之前；其顺序受 schema 约束。

生成接受全部修订的干净副本：`python scripts/accept_changes.py in.docx out.docx`（注意：accept_changes.py 走 LibreOffice，无 soffice 时不可用 — Windows 上可用 Word COM 的 `doc.AcceptAllChanges()` 替代）。

接受被删除的段落标记应把该段并入下一段，因此 run 全被删除的段落会整段消失。Word 是这么做的；`accept_changes.py` 和 `pandoc --track-changes=accept` 不总是。两者同样失败：剥掉删除文本但留下空段落，若是自动编号段就读成一个多余的空 bullet：

- `pandoc --track-changes=accept` 从不并段。
- `accept_changes.py`（LibreOffice）并段正确，除非被删段后面紧跟一个空的间隔段。

任一视图中的空 bullet 是该视图的产物，不是文档缺陷。在 XML 里核对段落删除。

## 批注（Comments）

批注需要六个交叉链接的文件。用 helper — 若同时要改 `document.xml` 用目录模式（省一次解压/压缩循环），否则用 `.docx` 直连模式：

```bash
# 对已解包目录（推荐，同时要放标记时）
python scripts/comment.py unpacked/ "费用上限过低"
python scripts/comment.py unpacked/ "同意" --parent 0

# 直接对 .docx
python scripts/comment.py contract.docx "This cap is too low" -o annotated.docx
```

脚本写 `comments.xml`、`commentsExtended.xml`、`commentsIds.xml`、`commentsExtensible.xml`、关系文件和 content-type override。批注 ID 自动分配。然后它打印要加进 `word/document.xml` 的 `<w:commentRangeStart>`/`<w:commentRangeEnd>`/`<w:commentReference>` 片段，让批注锚定到具体文本 — 不放这些标记，批注存在但不可见。

## 依赖

`docx` (npm) · `pandoc` · `defusedxml` (pip) · LibreOffice (`soffice`) · `pdftoppm` (Poppler)
环境要求：Node（`npm install docx`）· Python（`pip install defusedxml`）· pandoc/LibreOffice/Poppler 缺失时按上文替代方案走；读取按 SKILL.md 决策规则：工具在用工具，不在走 COM。
