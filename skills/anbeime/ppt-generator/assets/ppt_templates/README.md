# PPT 样式模板配置

本目录用于存放 PPT 的自定义样式模板文件。

当前版本使用默认样式，如需自定义字体、颜色、主题等，可以在此添加配置文件。

## 模板文件格式（待扩展）

未来版本支持通过以下方式自定义 PPT 样式：

1. **颜色主题配置**
   - 定义主色调、辅助色、强调色等

2. **字体配置**
   - 定义标题字体、正文字体、字号等

3. **布局模板**
   - 自定义幻灯片布局

## 使用方法（规划中）

```bash
python scripts/generate_pptx.py \
  --input ./ppt_data.json \
  --output ./presentation.pptx \
  --template ./assets/ppt_templates/custom_theme.json
```

## 默认样式说明

当前版本使用 python-pptx 的默认样式：
- 字体：Calibri (中文使用微软雅黑)
- 标题字号：36pt
- 正文字号：20pt
- 颜色：主题色为蓝色

<!-- ERIC-AUTHOR-INFO:START -->
---

## 📬 作者信息

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | gyc567@gmail.com |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | 360369487 |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->
