# Skill 仓库维护与一致性闸门 · skill-repo-maintenance

> **把"人工目测才会发现"的问题，全部变成机器闸门。**
> 沉淀自 136 个 Skill 的一次全面返工复盘。
> 品牌化改造：AI Skills 创作小店

[![许可](https://img.shields.io/badge/许可-MIT-blue)](https://opensource.org/licenses/MIT)
[![依赖](https://img.shields.io/badge/依赖-零%20纯标准库-blue)]()
[![实测](https://img.shields.io/badge/漂移-543%20%E8%A2%AB%E6%8D%BB%E6%89%80-green)]()

---

## ⚡ 30 秒上手

```bash
# 检查（CI 友好，rc=1 = 有问题）
python3 scripts/check_repo.py --check

# 自动修 README 计数
python3 scripts/check_repo.py --fix

# 同步到全部 5 个 AI 工具
python3 scripts/sync_skills.py
```

---

## 📊 实测：这套闸门抓到了什么

| 问题 | 规模 |
|------|------|
| README 计数与实际不符 | 声明 124，实际 **136** |
| Skill 未在 README 表格中列出 | **95 个** |
| 缺 `SKILL.md` / `name` 不匹配目录名 | **20 个** |
| 缺 LICENSE | **119 个** |
| **真实 API Key 混进仓库** | **4 处** |
| 各工具目录内容漂移 | **543 处** |

**543 → 0**（同步后复检通过）。

---

## 📁 内容

```
skill-repo-maintenance/
├── SKILL.md                    # 主流程 + 判定表 + 许可红线
├── README.md                   # 本文件
├── LICENSE                     # MIT
└── scripts/
    ├── check_repo.py           # 一致性闸门（10 项检查）
    └── sync_skills.py          # 多端统一同步（指纹比对）
```

---

## 🎯 设计的核心思路

| 原则 | 实现 |
|------|------|
| **单一真源** | 仓库 `skills/` 是真源，5 个工具目录都是脚本维护的镜像 |
| **内容指纹比对** | 忽略 mtime，只看文件内容 —— 跨机器可比 |
| **先删后拷** | 避免上游删掉的文件残留在目标端 |
| **宁误报不漏报** | 凭据扫描用宽松白名单，宁可多报 |
| **可自动修的别手改** | README 计数交给 `--fix` |

---

## 📜 许可与来源

| 项 | 说明 |
|----|------|
| **作者** | ERIC（AI Skills 创作小店） |
| **许可** | MIT License |
| **原创性** | 原创编写 —— 基于 great-skill-center 的真实返工数据 |

---

## 📞 定制化开发

如需**定制化开发**（多仓库同步、CI 集成、自定义凭据规则、体积优化），可直接联系 ERIC：

| 项 | 联系方式 |
|----|---------|
| **作者定位** | ERIC AI技术专家，专注于人工智能和自动化工具的研究与应用 |
| 邮箱 | `gyc567@gmail.com` |
| Twitter | `@EricBlock2100` |
| 微信 | `360369487` |
| Telegram | https://t.me/fatoshi_block |
| Telegram 频道 | https://t.me/cryptochanneleric |
| 加密情报 TG 群 | https://t.me/btcgogopen |
| YouTube 频道 | `@0XBitFinance` |
| 个人技术博客 | `topdigg.com` |

> **品牌**：AI Skills 创作小店
> 如需定制化开发，可直接联系 ERIC。

---

## 🔗 相关

- **AI Skills 创作小店** — https://github.com/gyc567/great-skill-center
- 仓库规则全文：`PROJECT_RULES.md`
