# 简历报告 Skill

锐仕方达猎头简历报告制作规范，支持多平台 AI Agent 使用。

## 📦 获取方式

### 在线查看
https://github.com/youhan1202/hermes-resume-skill

### 下载 ZIP
https://github.com/youhan1202/hermes-resume-skill/archive/refs/heads/main.zip

## 🚀 各平台安装

### Hermes Agent
```bash
hermes skills tap add https://github.com/youhan1202/hermes-resume-skill
hermes skills install risfond-resume-report
```

### Coze / Dify / 其他平台
1. 下载 ZIP 包
2. 解压后读取 `risfond-resume-report/SKILL.md` 内容
3. 将内容复制到你的 AI Agent 的 prompt/知识库/系统指令中

### 手动使用
直接复制 `risfond-resume-report/SKILL.md` 到任何支持自定义 prompt 的 AI 平台

## 📁 文件说明

```
risfond-resume-report/
├── SKILL.md                    # 核心规范（必读）
├── references/                 # 参考文档
│   ├── candidate-file-reading.md      # 读取候选人简历方法
│   ├── eight-sample-analysis.md       # 8份样本分析
│   ├── reading-old-doc-files.md       # 旧版 .doc 文件处理
│   ├── subagent-prompt-template.md    # 子代理提示词模板
│   └── windows-quirks.md             # Windows 环境注意事项
└── scripts/
    └── gen_resume_report.py    # Python 生成脚本模板
```

## ✨ 功能特性

- 自动分析候选人简历（PDF/DOC/DOCX）
- 生成标准化简历报告（.docx）
- 核心优势提炼与确认
- 排版格式严格遵循锐仕方达规范
- 支持多模型协作（DeepSeek + 豆包等）

## 📋 核心规范要点

1. **排版结构**: 标题区 → 基本信息 → 综合评估 → 教育背景 → 工作经历 → 尾部声明
2. **字体格式**: 宋体 10.5pt，标题 12pt Bold，行距 1.15 倍
3. **颜色规范**: 工作经历标题行 #2E75B5（蓝色），汇报对象/下属人数 #000000
4. **核心优势**: 3-4 条，突出 0-1 经验、产值规模、行业关键词
5. **【】标签**: 默认不加粗（以参考文件为准）
6. **图片规则**: 有参考文件时默认使用其标题图片，无参考文件时纯文字
7. **薪资格式**: XXk*X薪=XXw税前

## 🎯 使用流程

1. 提供候选人简历文件（PDF/DOC/DOCX）
2. AI 分析简历，输出核心优势草稿供确认
3. 确认后生成完整简历报告（.docx）
4. 自动打开文件供查看

## 📝 注意事项

- 【】标签默认不加粗
- 公司介绍内容不加粗
- 教育背景：五号字、1.5倍行距、无段前距、无开头空格
- 基本信息：字段之间不要空行
- 职业经历时长紧跟在时间后面
- 已离职写“离职原因”，在职写“看机会原因”
- 有参考文件时默认提取其模块标题图片作为标题
- 不添加锐仕方达企业logo和装饰性分隔线图片
- 非统招本科不写入核心优势（通过教育经历时间线判断）
- 年营收不能跨公司合计，应在各段工作经历中分别标注
- 0-1 工厂建设经验是核心卖点，必须突出
- 产值/规模数据前置（年营收 X 亿、项目规模 X 万吨）

## 🔗 相关链接

- GitHub 仓库: https://github.com/youhan1202/hermes-resume-skill
- Hermes Agent: https://hermes-agent.nousresearch.com/
