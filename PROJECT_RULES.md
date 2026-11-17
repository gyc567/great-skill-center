# great-skill-center 项目规则

> 这些规则不是建议，是**闸门**。违反会被 `scripts/check_repo.py` 直接拦下。
> 每一条都对应一次真实返工。
> 规则版本：v1.0（2026-11-13）· 来源：126 个 Skill 的一次全面返工复盘

## 0. 单一真源（Single Source of Truth）

**仓库 `skills/` 目录是唯一真源。** 所有 AI 工具目录都是**镜像**，由脚本维护，绝不手工编辑。

```
/root/repos/great-skill-center/skills/    ← 真源
        │
        │  python3 scripts/sync_skills.py
        ▼
  ┌─────────────┬─────────────┬─────────────┬─────────────┐
  │ .hermes/    │ .claude/    │ .openclaw/  │ .codex/     │
  │ skills/     │ skills/     │ skills/     │ skills/     │
  └─────────────┴─────────────┴─────────────┴─────────────┘
                   (+ .agents/skills)
```

| 规则 | 理由 |
|------|------|
| 永远不手工 `cp` 到工具目录 | 实测曾有 **543 处漂移**（136 个 Skill 里只有 1 个装在全部 5 端） |
| 改完 Skill 必跑 `sync_skills.py` | 否则出现"hermes 有、claude 没有"的幽灵安装 |
| 提交前跑 `check_repo.py --check` | 退出码 1 = 有漂移，CI 友好 |

## 1. 新增 Skill 的标准流程

```bash
# 1. 安装上游（登记在 sync_skills.py 的 SKILL_SOURCES）
python3 scripts/sync_skills.py --install <name>

# 2. 品牌化改造（用户可见文本 → AI Skills 创作小店）
#    ⚠️ 保留功能性标识：命令名/路径/环境变量/包名/协议标识/上游署名

# 3. 补 LICENSE（上游许可原文 + 品牌说明）
#    补 README.md（品牌化 + ERIC 联系方式）

# 4. 更新根 README 表格与计数
python3 scripts/check_repo.py --fix      # 自动修计数

# 5. 同步到所有工具
python3 scripts/sync_skills.py

# 6. 闸门
python3 scripts/check_repo.py --check    # 必须 rc=0

# 7. 提交
git add -A && git commit -m "..." && git push ssh-origin main
```

## 2. 品牌化改造规则

| 类别 | 处理 | 例子 |
|------|------|------|
| **用户可见的展示文本** | ✅ 换成「AI Skills 创作小店」 | 页面标题、页脚署名、CLI 横幅、`<meta generator>` |
| **功能性标识** | ❌ 保留原样 | 命令名、数据目录、环境变量、npm 包名、插件名、协议标识 |
| **事实性上游来源** | ❌ 保留（MIT 等许可要求） | 上游 GitHub URL、作者署名、许可声明 |
| **路径示例** | ⚠️ 保留但**不能是个人路径** | `C:/Users/Name/...` 是示例，OK；`/Users/gyc567/...` 要改 |

**判定标准**：改了会**导致功能坏掉**的 → 保留；改了只是**用户看到的样子**的 → 换。

## 3. 凭据红线

**任何 API Key / Token / Cookie / 密码都不得进入仓库、README、Skill、提交信息或报告。**

- 引用一律写 `[REDACTED]`
- 上游带来的示例 key 也要替换成 `YOUR_KEY_HERE` 占位符
- `check_repo.py` 会扫：GitHub PAT / Anthropic / OpenAI / AWS / Google / Slack / JWT / 通用 `key=xxx` 模式
- ⚠️ **实测曾有上游 anbeime 的真实 Coze key 混进来（4 处）** —— 复制上游代码时必须扫一遍

## 4. 许可红线

| 上游许可 | 能否商用/上架 | 处置 |
|---------|------------|------|
| MIT / Apache-2.0 / BSD | ✅ | 复制 + 保留许可原文与署名 |
| **PolyForm Noncommercial** | ⚠️ **看历史版本** | 若上游曾改许可，**变更前的 MIT 版本永久有效**（需核实并留存快照） |
| GPL | ⚠️ | 衍生作品须同许可发布 |
| AGPL | ❌ 慎用 | 网络服务也要开源 |
| 无 LICENSE | ❌ **不可入库** | 仅作参考，不复制代码 |

**上架 SkillPay 的前提**：必须有明确的可商用许可。

## 5. 质量闸门（可机械判定的，绝不靠人眼）

| 检查 | 工具 |
|------|------|
| Skill 结构、frontmatter name == 目录名 | `check_repo.py` |
| README 计数 / badge / 表格完整性 | `check_repo.py --fix` |
| 凭据泄露 | `check_repo.py` |
| 各工具目录一致性 | `check_repo.py --check` / `sync_skills.py` |
| Skill 内部逻辑（如话术是否符合 FABE） | **每个 Skill 自带校验器** |

> 💡 **写 Skill 的核心原则**：不要只讲理论 —— 配一个**能机械判定的校验器**，
> 并**用正反例双向验证**它真的在拦人。
> 反向验证 = 把合规内容改坏，确认校验器从 PASS 变 FAIL。

## 6. 写 Skill 的反模式

| ❌ 别做 | ✅ 改做 |
|--------|--------|
| 讲一遍理论就完事 | 配校验器 + 测试套件 |
| 只测正例 | **正例 + 反例双向验证** |
| 校验词典一次写死 | 词典按行业扩充，且**用真实内容测出缺口** |
| 一次性脚本 | 沉淀成 `scripts/` 下的可复用工具 |
| 手写 README 计数 | 交给 `--fix` 自动生成 |

## 7. 提交规范

```bash
git config user.name  "gyc567"          # 已是全局默认
git config user.email "gyc567@gmail.com"
git push ssh-origin main                # SSH 推送（HTTPS 会 401）
```

- 提交前：`check_repo.py --check`（rc=0）+ `sync_skills.py`
- 推送后：验证 GitHub 在线文件 HTTP 200 + 署名是 `gyc567`
- 提交信息用中文，格式：`feat: 新增 xxx —— 一句话说明`

## 8. 不熟悉的技术：先检索再实现

> 遇到不熟悉的功能，**不要从零实现**。
> 先检索 GitHub 上维护活跃、许可证明确的同类开源项目，比较实现思路、依赖和已知问题，
> 优先借鉴已验证的设计，**不复制**许可证不兼容、来源不明、技术栈冲突或含危险操作的代码。

**验证优先级**：
1. 上游自带测试 → 跑一遍（`python3 -m unittest discover -s tests`）
2. 品牌化改造后**重跑**测试 → 证明改造没破坏功能
3. 真实渲染/执行一次 → 不只看 `--help`

## 9. ERIC 署名（对外分发的 Skill）

每个 Skill 的 README / SKILL.md 末尾必须包含：

> **ERIC** · AI技术专家，专注于人工智能和自动化工具的研究与应用
> 邮箱 `gyc567@gmail.com` · Twitter `@EricBlock2100` · 微信 `360369487`
> Telegram https://t.me/fatoshi_block · 频道 https://t.me/cryptochanneleric
> 加密情报群 https://t.me/btcgogopen · YouTube `@0XBitFinance` · 博客 `topdigg.com`
>
> 品牌：**AI Skills 创作小店** · 如需定制化开发，可直接联系 ERIC。

---

## 附：返工根因速查（2026-11-13 复盘）

| 现象 | 根因 | 根治手段 |
|------|------|-----------|
| README 计数漂移 12 个 | 计数手写三处 | `check_repo.py --fix` |
| 543 处多端漂移 | 手工 cp | `sync_skills.py` |
| 真实 Coze key 进仓库 | 复制上游代码不扫描 | `check_repo.py` 凭据扫描 |
| 95 个 Skill 不在 README 表格 | 表格手维护 | `check_repo.py` 表格完整性 |
| 20 个 Skill 缺 SKILL.md / name 不匹配 | 装上游时没校验 | `check_repo.py` frontmatter 检查 |
| 119 个 Skill 缺 LICENSE | 装上游时没抄许可 | `check_repo.py` license 警告 |
| 自写脚本自己出 bug | 写完不测 | 每个脚本自带测试 + 先跑再提交 |
| 校验器词典有缺口 | 只测正例 | 正反例双向验证 + 真实内容测试 |

