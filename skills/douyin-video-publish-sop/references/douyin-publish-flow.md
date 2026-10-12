# 抖音创作者中心发布流程（Browser Use 实测版）

> 本文件是 SKILL.md「发布」一节的详细操作手册，按 Browser Use（`computer_use_tool` plane="bu"）实测整理。核心纪律：**登录与短信验证必须交接用户，绝不代填验证码；发布是外部副作用动作，用户已明确授权时执行，否则先交接确认。**

## 0. 前置

- 视频成品已就绪（mp4 本地路径）。
- 若未登录：打开 https://creator.douyin.com/creator-micro/content/upload，读到"扫码登录/验证码登录"即为登录阻塞 → 立即 `interaction.request_action(type="browserControl")`，等用户扫码后 `bu.resync()` 重读。
- 登录成功标志：URL 变为 `.../creator-micro/home` 且页面上出现账号名与"作品发布"。

## 1. 进入发布页并上传

```python
bu.navigate("https://creator.douyin.com/creator-micro/content/upload")
bu.wait_for_load(timeout=20)
snap = bu.snapshot()          # 找 input[type=file]（accept 含 video/mp4）
bu.upload(ref_or_selector, "/abs/path/video.mp4")
```

- 上传后页面会跳转到 `.../content/post/video?enter_from=publish_page` 表单页；等待处理完成（可 sleep 10s 后 snapshot）。

## 2. 填写基础信息

- **标题**（≤30 字，情绪钩子 + 前置核心词）：`bu.type(title_input_ref, "40岁老板失业，假装上班三个月，出路在哪？")`
- **话题**（3-4 个，踩坑点！）：点开话题输入区（`#添加话题`）后，**每个话题必须输入 `#词` 再按 Enter 逐个确认**；只输入不带 # 的文本不会变成标签，`ctrl+a+Backspace` 可清空未确认文本。
- **正文**（≤1000 字）：话题确认后在同一富文本区末尾（`End` 键）追加场景化正文 + CTA（评论区扣 1）。

## 3. 封面

- 点"选择封面"→ 弹层有"设置竖封面/设置横封面"。
- **竖封面**：直接 `bu.upload_file("input[type=file][accept*='image/png']", cards/c1.png)` 上传首帧卡（最强钩子帧）；上传后点弹层"完成"保存。
- **横封面**：可点"设置横封面"独立设置，或选"暂不设置"让平台提示"已基于竖封面生成横封面"（实测平台会自动生成，无需额外操作）。

## 4. 自主声明

- 点"自主声明"→ 弹层选 **"内容由AI生成"**（本 SOP 产物为 AI 辅助创作，如实声明）→ 点"确定"。
- 声明后发布页显示"自主声明 内容由AI生成"。

## 5. 发布与短信验证（关键踩坑点）

```python
bu.click(publish_button_ref)   # 第一层"完成"→ 进入最终发布确认页
```

- 最终确认页有"发布/暂存离开"按钮，点 **"发布"**。
- **实测**：点发布后大概率弹出**接收短信验证码弹窗**（"为确保是本人操作抖音账号，请输入当前手机号收到的短信验证码"）→ 这是身份验证 checkpoint，**立即** `interaction.request_action(type="browserControl")`，提示用户：点"获取验证码"→ 手机查收 → 填验证码 → 点"验证"。**绝不代收/代填验证码。**
- 验证通过后 URL 自动跳转 `.../content/manage?enter_from=publish`（内容管理页）。

## 6. 审核确认

- 内容管理页刚发布作品状态为 **"审核中"**（正常）；刷新后确认出现新作品：标题、时长、发布时间。
- 向用户汇报：作品标题、账号、发布时间、审核状态。

## 7. 常见状态速查

| 页面/状态 | 含义 | 处理 |
|---|---|---|
| `blocked=auth` / 扫码登录页 | 未登录 | 交接用户扫码 |
| 发布页停在原 URL 且无跳转 | 可能弹了短信验证 | snapshot 找"接收短信验证码"弹窗 → 交接 |
| `content/manage` + 新作品"审核中" | 发布成功，审核中 | 刷新确认后汇报 |
| 发布页提示"作品上传中请勿关闭" | 上传/转码中 | 等待后重读 |
| 发文助手"作品未见异常" | 合规检测通过 | 直接发布 |

## 8. 发布配套（流量优化）

- 话题前 3 位放核心搜索词；正文首段复述核心词；置顶评论发布后补 1-3 个核心词（看后搜联动）。
- 封面卡 1 用最强钩子帧；发文助手"封面优化建议"非阻断项，可发布后迭代。
