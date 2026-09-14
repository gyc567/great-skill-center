# 候选人简历文件读取指南

候选人提供的原始简历文件有三种常见格式，读取方法如下：

## 1. PDF (.pdf)
```python
import fitz  # PyMuPDF，导入名也可以是 pymupdf
doc = fitz.open("简历.pdf")
for page in doc:
    text = page.get_text()
doc.close()
```
- 需要先装：`pip install pymupdf`
- 注意：PyMuPDF 的包名是 `pymupdf`，但导入时通常用 `import fitz`

## 2. DOCX (.docx) — 新版Word
```python
from docx import Document
doc = Document("简历.docx")
for p in doc.paragraphs:
    text = p.text
```
- python-docx 自带，无需额外安装

## 3. DOC (.doc) — 旧版Word（分析格式用）
旧版 .doc 无法直接用 python-docx 读取，需要转换后再分析：

```powershell
# 用 Word COM 转存为 .docx
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("源文件.doc")
$doc.SaveAs([ref]"目标文件.docx", [ref]16)  # 16 = wdFormatXMLDocument
$doc.Close()
$word.Quit()

# 再用 python-docx 分析
from docx import Document
doc = Document("目标文件.docx")
for p in doc.paragraphs:
    for r in p.runs:
        # 检查颜色
        try: c = str(r.font.color.rgb)
        except: c = 'theme'
        print(f'[B={r.bold} sz={r.font.size} c={c}] {r.text[:60]}')
```

## 4. 注意事项
- PDF 可能扫描件（图片），需要 OCR。目前不支持。
- .doc 文件用 ComObject 读取文本时可能报 RPC 错误（0x800706BE），先杀掉所有 WINWORD 进程再试，或换文件。
- ⚠️ **不要用 olefile 直接解析 .doc 文本**——提取结果严重乱码，不可用。必须用 Word COM 中转。
- python-docx 读取 .doc 会报 Package not found，必须用 ComObject 中转。
