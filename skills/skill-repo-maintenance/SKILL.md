---
name: skill-repo-maintenance
description: 维护 Skill 仓库时使用 —— 新增/更新 Skill 的标准流程、多工具目录统一同步、README 计数自动维护、凭据泄露扫描、frontmatter 与许可证完整性检查。当用户要求"安装新 skill""同步到所有 AI 工具""检查仓库""提交前验证""扫描密钥泄露"或提到 skill 仓库维护/上架前检查时使用。包含可一键运行的一致性闸门脚本。  Use when maintaining a Skill repository: installing/updating skills, syncing to multiple AI tool directories, keeping README counts correct, scanning for leaked credentials, validating frontmatter and licenses. Ships with runnable consistency-gate scripts.
---

# Skill 仓库维护与一致性闸门

> 品牌：AI Skills 创作小店
> 本 Skill 沉淀自 **136 个 Skill 的一次全面返工复盘** —— 每条规则都对应一次真实踩坑。

---

## 一、为什么需要这套东西

在 great-skill-center（136 个 Skill、5 个 AI 工具目录）上实测：

| 问题 | 规模 |
|------|------|
| README 计数与实际不符 | 声明 124，实际 136 |
| Skill 未在 README 表格中列出 | **95 个** |
| 缺 `SKILL.md` 或 `name` 与目录名不匹配 | **20 个** |
| 缺 LICENSE | **119 个** |
| **真实 API Key 混进仓库** | **4 处**（上游带来的） |
| 各工具目录内容漂移 | **543 处** |

**根因只有一个：这些全是"人工目测才会发现"的事。**
解法也只有一个：**把它们变成机器闸门。**

---

## 二、三个脚本

### 1. `scripts/check_repo.py` —— 一致性闸门

```bash
python3 scripts/check_repo.py            # 全量检查，rc=1 表示有问题
python3 scripts/check_repo.py --fix      # 自动修 README 计数
python3 scripts/check_repo.py --check    # 只检查（CI 用）
```

**检查项**：

| 检查 | 级别 | 说明 |
|------|------|------|
| `SKILL.md` 存在 | ❌ 错误 | 打包前必须有 |
| frontmatter `name` == 目录名 | ❌ 错误 | 不一致会导致 Skill 加载失败 |
| frontmatter `description` 存在 | ⚠️ 警告 | 影响 Skill 被检索到的概率 |
| README 计数 == 实际目录数 | ❌ 错误 | `--fix` 可自动修 |
| README badge 数字一致 | ❌ 错误 | 同上 |
| README 表格覆盖所有 Skill | ❌ 错误 | 漏了用户就看不到 |
| 表格无对应目录 | ⚠️ 警告 | 可能有已删除的残留 |
| **凭据泄露** | ❌ 错误 | GitHub PAT / Anthropic / OpenAI / AWS / Google / Slack / JWT / 通用 key= |
| LICENSE 存在 | ⚠️ 警告 | 上架前提 |
| ERIC 联系方式 | ⚠️ 警告 | 项目规则 |
| 各工具目录一致性 | ❌ 错误 | 复用 `sync_skills.py` 的指纹逻辑 |

**凭据扫描的白名单**（避免误报）：
- `REDACTED` / `xxxxxxxx` / `your_key` / `placeholder` / `<...>`
- `sk-test` / `sk-invalid` / `sk-fake` / `sk-probe`
- `example.com` / `127.0.0.1` / `localhost`
- `tests/` `examples/` `templates/` `.md` 目录（示例文档允许）

### 2. `scripts/sync_skills.py` —— 多端统一同步

```bash
python3 scripts/sync_skills.py              # 同步全部
python3 scripts/sync_skills.py --check      # 只查漂移（rc=1 = 有漂移）
python3 scripts/sync_skills.py cinecode    # 只同步指定
python3 scripts/sync_skills.py --install    # 从上游 git 源安装
python3 scripts/sync_skills.py --list       # 列出所有 Skill 及各端状态
python3 scripts/sync_skills.py --include-large   # 含大体积 Skill
```

**关键设计**：
- **内容指纹比对** —— 忽略 mtime，只看文件内容，跨机器可比
- **先删后拷** —— 避免上游删掉的文件残留在目标端
- **默认跳过 > 8MB 的 Skill** —— 需要时 `--include-large`
- **支持 `--install`** —— 上游源登记在 `SKILL_SOURCES` 字典里

### 3. 二者配合

```bash
python3 scripts/check_repo.py --fix     # 1. 修计数
python3 scripts/sync_skills.py         # 2. 同步
python3 scripts/check_repo.py --check  # 3. 验证（rc=0）
```

---

## 三、标准流程（新增 Skill）

```bash
# 1. 安装上游
python3 scripts/sync_skills.py --install <name>

# 2. 品牌化改造
#    ✅ 用户可见文本 → AI Skills 创作小店
#    ❌ 命令名/路径/环境变量/包名/协议标识/上游署名 保持原样

# 3. 补 LICENSE + README（品牌化 + ERIC 联系方式）

# 4. 更新根 README
python3 scripts/check_repo.py --fix

# 5. 同步 + 验证
python3 scripts/sync_skills.py
python3 scripts/check_repo.py --check    # 必须 rc=0

# 6. 提交
git add -A && git commit -m "feat: 新增 xxx" && git push ssh-origin main
```

---

## 四、品牌化改造判定表

| 类别 | 处理 | 例子 |
|------|------|------|
| 用户可见的展示文本 | ✅ 换 | 页面标题、页脚署名、CLI 横幅、`<meta generator>` |
| 功能性标识 | ❌ 保留 | 命令名、数据目录、环境变量、npm 包名、插件名、协议标识 |
| 事实性上游来源 | ❌ 保留 | 上游 GitHub URL、作者署名、许可声明 |
| 路径示例 | ⚠️ 保留但非个人 | `C:/Users/Name/...` OK；`/Users/gyc567/...` 要改 |

**判定标准**：改了会**导致功能坏掉**的 → 保留；改了只是**用户看到的样子**的 → 换。

---

## 五、许可红线

| 上游许可 | 可商用/上架 | 处置 |
|---------|-----------|------|
| MIT / Apache-2.0 / BSD | ✅ | 复制 + 保留许可原文与署名 |
| PolyForm Noncommercial | ⚠️ 看历史版本 | 上游改过许可时，**变更前的 MIT 版本永久有效**（核实并留存快照） |
| GPL | ⚠️ | 衍生作品须同许可 |
| AGPL | ❌ 慎用 | 网络服务也要开源 |
| 无 LICENSE | ❌ **不可入库** | 仅作参考，不复制代码 |

---

## 六、返工根因速查

| 现象 | 根因 | 根治手段 |
|------|------|---------|
| README 计数漂移 | 计数手写多处 | `check_repo.py --fix` |
| 多端漂移 | 手工 cp | `sync_skills.py` |
| 真实 Key 进仓库 | 复制上游代码不扫描 | `check_repo.py` 凭据扫描 |
| Skill 不在 README 表格 | 表格手维护 | `check_repo.py` 表格完整性 |
| 缺 SKILL.md / name 不匹配 | 装上游不校验 | `check_repo.py` frontmatter 检查 |
| 自写脚本自己出 bug | 写完不测 | 每个脚本自带测试 + 先跑再提交 |
| 校验器词典有缺口 | 只测正例 | **正反例双向验证** |

---

## 七、原则

1. **可机械判定的，绝不靠人眼。**
2. **单一真源**，其余全是镜像。
3. **正反例双向验证** —— 把合规内容改坏，确认校验器从 PASS 变 FAIL。
4. **复制上游代码必扫密钥** —— 上游自带的"示例 key"经常是真 key。
5. **写完脚本先跑再提交** —— 我自己就写出过 `endswith(set)` 的 TypeError。

---

> **品牌**：AI Skills 创作小店
> 如需定制化开发，可直接联系 ERIC：gyc567@gmail.com
> Twitter `@EricBlock2100` · 微信 `360369487` · Telegram https://t.me/fatoshi_block
> 博客 `topdigg.com`
