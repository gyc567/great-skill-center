# XLSX 创建、编辑与分析

> 脚本路径均相对本 skill 根目录。
> **Windows + Office 环境适配（工具缺失时）**：
> - `openpyxl`/`pandas` 多数环境**未预装**：`pip install openpyxl pandas` 后直接用。
> - `scripts/recalc.py` 依赖 LibreOffice，无 soffice 时不可用。**Windows 重算走 Excel COM**（PowerShell）：
>   ```powershell
>   $xl = New-Object -ComObject Excel.Application; $xl.Visible = $false
>   $wb = $xl.Workbooks.Open("D:\path\file.xlsx")   # 默认自动重算并缓存
>   $xl.CalculateFullRebuild(); $wb.Save(); $wb.Close($false); $xl.Quit()
>   ```
>   （同样遵守 COM 清理铁律：`Quit()` + `ReleaseComObject` + `GC::Collect`，见 SKILL.md。）
> - `markitdown` 缺失时（pip 可装）：快速浏览用 `scripts/extract_office_text.ps1`；精确读（带坐标）直接 `pip install openpyxl pandas`。

| 任务 | 路线 |
|---|---|
| 带**公式/格式**的创建或编辑 | `openpyxl` — 见下方坑点 |
| **批量数据**进出 | `pandas`（`read_excel`、`to_excel`） |
| **快速看一眼**某表 | `markitdown file.xlsx` — 每 sheet 一段 `## SheetName`，也读 `.xlsm`（无单元格坐标，别拿它规划编辑）；不在则 `scripts/extract_office_text.ps1`（逐 sheet 制表符分隔） |
| **读模型**（公式*和*值） | 两次 `load_workbook` — 见下方坑点 |
| **精确读/规划编辑** | `openpyxl`（pip 一装即有，带单元格坐标；COM 提取没有坐标） |

读取决策规则（官方工具 vs COM）见 SKILL.md"读取路线怎么选"。

> `openpyxl`、`pandas` 在预装环境直接用；未预装的 `pip install` 后再导入。导入失败（或 `markitdown` 命令缺失）时装对应包。

## 每个输出的硬性要求

- **专业字体**（Arial、Times New Roman）贯穿全表，除非用户另有说明。
- **零公式错误。** 重算报错时绝不交付。若怀疑错误在你之前就存在，自证：用 `data_only=True` 加载*原始*文件看那个单元格。你引入的错误和你继承的错误长得一模一样。
- **用公式，绝不硬编码结果。** 写 `sheet['B10'] = '=SUM(B2:B9)'`，不是 Python 算好的总数。表必须随输入变化重新计算。
- **逐字遵循用户规格。** 精确的 tab 名、精确的列头、用户拼出的公式。一个计算别的东西的重设计再优雅也算失败。
- **把每个假设和硬编码数字记在读者看得到的地方** — 单元格批注，或表尾相邻单元格。有真实来源就引用（`Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]`）；数字来自用户就直说。
- **你创建的、给人填的工作簿**需要简短图例说明哪些单元格要编辑，加一行真实数值的示例行展示期望格式。绝不往别人要你编辑的文件里加这种行。
- **编辑现有文件：精确匹配它的惯例。** 惯例优先于本文档一切指导。先找它指定的输入单元格 — 特殊字体色、填充或底纹标记的那些 — 只往那里写，且不碰任何现有公式。

## 重算（文件含公式时必做）

openpyxl 把公式写作**无缓存值**的字符串。重算之前，任何读缓存值的东西 — `pandas`、`load_workbook(data_only=True)`、多数预览器 — 读到的公式单元格全是 `None`。

```bash
python scripts/recalc.py output.xlsx [timeout_seconds]   # 默认 30；需 LibreOffice
```

LibreOffice 算完所有公式，文件**原地重写**，输出 JSON：`status`（`success` | `errors_found`）、`total_formulas`、`total_errors`、`error_summary`（每类错误最多点 100 个单元格，`locations_truncated` 说明扣了多少 — 信 `total_errors`，别信列表长度）。修完它点名的再跑。**JSON 里是 `error` 键而非 `status` 键 = 什么都没重算**，只有这种情况退出码非零 — `errors_found` 退出码是 0，所以绝不把干净退出当干净工作簿。

无 LibreOffice 的 Windows 机器用顶部"环境适配"里的 Excel COM 重算；重算后可用 `data_only=True` 检查错误值（`#REF!` 等）。

**重算绿了证明公式*能求值*，不代表*算得对*。** 差一行的区间或引用错行，产出的是零错误但数字错的干净文件。先写 2-3 个公式核对取值符合预期，再铺满网格。

**链接其他文件的工作簿**，经 openpyxl 重存再重算会**丢链接**。这种公式读作 `='[1]Returns Analysis'!$B$2` — `[1]` 是工作簿外部引用列表的索引，指向*磁盘上的另一个文件*，不是 sheet。那个文件通常不在手边，所以单元格缓存值是唯一承载数据的东西。openpyxl 保存时剥掉该值；LibreOffice 只好真去解析引用，失败，写 `#NAME?`，并删除所有链接。`recalc.py` 在该状态下拒绝运行 — 先把那些单元格的值从原始文件拷出来再覆盖保存（`--force` 强制覆盖，接受损失）。

## 选能活过验证的公式

LibreOffice 实现的函数比 Excel 少，它算不了的一个会变成烧死在交付文件里的字面 `#NAME?`。（Windows 上用 Excel COM 重算无此限制，但文件若要在别处经 LibreOffice 处理——比如同事用 recalc.py——仍需遵守。）

- **优先 Excel 2007 时代函数** — `SUMIFS`、`INDEX`、`MATCH`、`IFERROR`、`SUMPRODUCT` — 无需前缀。
- **六个 2007 后函数可用，但必须带 `_xlfn.` 前缀**，因为 openpyxl 把公式原样写进 XML 而 Excel 存 2007 后名字时带前缀（UI 里隐藏）：`_xlfn.TEXTJOIN`、`_xlfn.CONCAT`、`_xlfn.IFS`、`_xlfn.SWITCH`、`_xlfn.MAXIFS`、`_xlfn.MINIFS`。裸写全变 `#NAME?`。
- **绝不用 `XLOOKUP`、`XMATCH`、`SORT`、`FILTER`、`UNIQUE`、`SEQUENCE`。** 老版 LibreOffice 在*任何*前缀下都算不出。新版本能算，但它们是溢出数组函数而 openpyxl 写的文件没有溢出元数据，只有区间左上格有值 — `recalc.py` 对截断结果报 `total_errors: 0`。查找用 `INDEX`/`MATCH`，排序、过滤、去重在 Python 里做完再写单元格。
- LibreOffice 解析不了的公式会被**小写**写回 — `#NAME?` 旁边的快速识别标志。

## openpyxl 坑点

- **读模型要两次加载。** `data_only=True` 给缓存值但公式没了；默认给公式字符串但没有值。一次加载给不了两者。
- **`data_only=True` 保存即破坏。** 那个工作簿没有公式了，保存会把每个公式永久替换成字面值。
- **openpyxl 刚写的文件上 `data_only=True` 全是 `None`** — 先重算。（结果为 `""` 的公式也读回 `None`。）
- **合并单元格：只写左上锚点。** 区间内其他单元格是 `.value` 只读的 `MergedCell`。
- **`.xlsm` 不传 `keep_vba=True` 会丢宏**（`load_workbook`）。
- **带空格的 sheet 名在跨表引用里必须加引号**：`='Assumptions Inputs'!$B$5`。不加引号求值为 `#VALUE!`。

## 财务模型

除非用户另有说明，或现有文件已是别的做法。

**颜色：** 硬编码输入和情景杠杆蓝字（`0,0,255`）· 公式黑字 · 链接其他表绿字（`0,128,0`）· 链接其他文件红字（`255,0,0`）· 关键假设和用户待填单元格黄底（`255,255,0`）。

**数字：** 货币 `$#,##0`，单位在表头点名（`Revenue ($mm)`）· 零渲染为 `-`，百分比同样（`$#,##0;($#,##0);-`）· 负数用括号 · 百分比 `0.0%`，**按小数存储**（`0.15` 渲染 `15.0%`；存 `15` 渲染 `1500.0%`）· 估值倍数 `0.0x` · 年份存文本（`"2024"`，绝不 `2,024`）。

**结构：** 每个假设在自己带标签的单元格，被用它的公式引用（`=B5*(1+$B$6)`，绝不 `=B5*1.05`）· 每个预测期公式保持一致，因为行中孤立的改动格是最常见的静默错误 · 给可能为零的分母加保护。

## 依赖

`openpyxl`、`pandas`、`markitdown` (pip) · LibreOffice（`scripts/office/soffice.py` 自动配置）
环境要求：Python（`pip install openpyxl pandas`）· LibreOffice（`recalc.py` 需要；Windows 无 LibreOffice 时走 Excel COM 重算，见顶部环境适配）· markitdown（pip 可装，缺失时用提取脚本）。
