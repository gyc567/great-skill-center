# 安全审计报告 — 导演 / 视频提示词技能包（4 个仓库）

**审计时间**：2026-10-12 23:40 (GMT+8)
**审计对象**：nolanx-ai/nolanx.ai · Mikefluff/skills · ZeroLu/awesome-seedance · jnMetaCode/ai-shortfilm-prompts
**审计方法**：GitHub API 拉取完整文件树 → curl 直下原始文件 → 静态读取全部内容（绝不执行）→ 危险模式扫描 → 字节级完整性校验
**执行摘要**：4 个仓库**全部为 P2（安全）**，无 P0 阻断项；安装 104 个文件，字节级校验**零偏差**。

---

## 一、总评分

| 仓库 | 星数 | 许可 | P0 | P1 | 结论 | 评分 |
|---|---|---|---|---|---|---|
| nolanx-ai/nolanx.ai | 2031 | MIT | 0 | 0 | ✅ 可用 | 96 |
| Mikefluff/skills | 24 | MIT | 0 | 1（已规避） | ✅ 可用（精简安装） | 90 |
| ZeroLu/awesome-seedance | 2681 | MIT | 0 | 0 | ✅ 可用 | 95 |
| jnMetaCode/ai-shortfilm-prompts | 464 | MIT | 0 | 0 | ✅ 可用 | 97 |

**P0 阻断项：0。P1 需关注项：1（Mikefluff 仓库级的 `--execute` 执行层，已通过精简安装规避）。**

---

## 二、P0 区（阻断）

**无。** 全部 4 个仓库的被安装内容中，未发现任何：
- `curl | bash` / `wget | sh` 下载即执行
- 读取 `~/.ssh`、`.env`、云凭证后外送
- `sudo rm -rf /` 类破坏性命令
- base64 编码隐藏载荷

被安装的 104 个文件**全部是纯 Markdown 文本**（提示词、方法论、风格定义），无一行可执行代码，无脚本文件。

---

## 三、P1 区（需关注）

### [已规避] Mikefluff/skills 的 `--execute` 自动执行层

原仓库（**不是被安装的部分**）存在以下机制，**我们未安装**：

| 发现 | 位置 | 说明 |
|---|---|---|
| `curl … \| bash` 一键安装 | `README.md:109`、`install.sh:5` | 上游推荐的安装方式，我们**未使用**，改为 curl 直下原始文件 |
| `sudo apt-get install ffmpeg` | `install.sh:320` | 安装脚本会调用 sudo |
| `pip install -r requirements.txt` | `install.sh:345-399` | 在 venv 内装依赖，非全局 |
| API 密钥文件 `~/.skills.env`（chmod 600） | `README.md:294` | `--execute` 模式读取 OPENAI / GEMINI / FAL / RUNWAY / KLING / SUNO 等密钥 |
| `python3 scripts/run.py --execute` 调付费视频 API | `video-prompt/SKILL.md:84` | 会真实发起付费生成请求（默认需确认成本，`--yes` 可跳过） |

**风险性质**：均为**合法的可选执行能力**，无恶意意图。属于"提供能力"而非"自动执行危险操作"，最高定级 P1。

**处置**：本次**只安装 `common/style-library/video/` 下的 12 个纯 Markdown 风格文件**（+ 索引 + 模板 + README），**不安装** `install.sh`、`scripts/run.py`、`.env.example`、`skills-keys` 等执行层。安装后的技能零脚本、零网络调用。

### 其余 3 仓库 P1 发现：无

---

## 四、信息性提醒（非风险项）

1. **ZeroLu/awesome-seedance 含赞助商链接**：README 内有 APIMart、Cyberbara 的推广链接与二维码。这是原作者的商业化内容，不影响功能，但**不构成安全风险**。文件内保留了原作者署名与来源链接（MIT 许可要求）。
2. **nolanx.ai 仓库自身是一个完整应用**：README 提到 `./dev.sh`、`pnpm build`、OpenRouter/FAL/ReelMind API 配置。这是**那个 Web 应用的部署说明**，与我们安装的 `.nolanx/skills/` 纯文档技能**完全无关**——我们只取了它的导演技能文档，没有取任何应用代码。
3. **零 IP 风险提示（已被原作者内置）**：Mikefluff 的 12 个风格文件**明确要求导演名字不得进入发给模型的提示词**，仅作人类选片书签；shortfilm-prompt 也内置了 IP 规避规则。这是**加分项**，降低你的商用侵权风险。
4. **awesome-seedance 的 `scripts/update_last_updated.sh`**：仅是一个给 README 加时间戳的维护脚本，无风险，**未安装**。

---

## 五、详细检查结果

| 检查维度 | 结果 |
|---|---|
| **命令执行** | 被安装内容：0 条可执行命令。仓库级：Mikefluff `install.sh` 含 sudo/pip（未安装） |
| **文件读写** | 被安装内容：无任何文件写入。`skills-styles`（未安装）会写 `~/.claude/style-library/` |
| **网络访问** | 被安装内容：0 次。Mikefluff `run.py --execute`（未安装）会调外部 API |
| **远程脚本** | 0 处。所有文件为静态 Markdown |
| **依赖安装** | 被安装内容：0 个依赖。全部零依赖 |
| **凭证/密钥** | 被安装内容：无。README 中提及的环境变量均为上游应用配置说明 |
| **供应链源** | 全部从 `raw.githubusercontent.com` 官方域直下，无第三方中转、无 `git+https://` 直接安装 |
| **许可合规** | 4 仓库均为 **MIT**，可自由使用/修改/分发 |

---

## 六、安装结果（104 文件，字节级校验零偏差）

| 技能名 | 文件数 | 体积 | 来源 |
|---|---|---|---|
| `nolanx-director-visual-language` | 21 | 92K | nolanx.ai `.nolanx/skills/` 全部 20 个导演子技能 + 我写的索引入口 |
| `video-director-styles` | 16 | 116K | Mikefluff `common/style-library/video/` 12 风格 + 索引 + 模板 + README + 我的入口 |
| `awesome-seedance` | 4 | 108K | ZeroLu README 中英双版 + 商用案例 + 我的入口 |
| `shortfilm-prompt` | 66 | 548K | jnMetaCode 官方 skill 原样（SKILL.md + 中文版 + 27 套模板中英 + 6 个示例） |

**校验方式**：逐个文件比对「实际字节数 vs GitHub API 返回的 blob size」，**104/104 完全一致，0 个不一致**。
**结构校验**：4 个技能均通过 WorkBuddy 官方 `quick_validate.py`，返回 `Skill is valid!`

---

## 七、审计结论

> **✅ 4 个技能全部为 P2（安全），可直接使用。**
>
> 全部内容为纯 Markdown 文档（提示词库、风格定义、方法论），无脚本、无网络调用、无凭证读取、无依赖安装。唯一 P1 项（Mikefluff 的 `--execute` 付费 API 执行层）已通过"只装风格文档、不装执行器"的方式规避。
>
> 所有文件经字节级校验与上游完全一致，无篡改。4 仓库均为 MIT 许可，商用合规。

**遗留建议**：
1. 若日后想启用 Mikefluff 的 `--execute`（真实调 API 出片），需单独评估，且应将密钥写入 `~/.skills.env` 而非提交到任何仓库。
2. 新装技能可能需**重载会话**才会被触发。
3. awesome-seedance 为社区合集，提示词内的赞助商链接与本技能功能无关，可忽略。
