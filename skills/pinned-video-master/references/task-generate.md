# 生成数字人视频（task-generate）

## 目的
用 HeyGen 生成 30 秒竖屏数字人视频。

## ⚠️ 前置门（不可跳过）
1. 逐字稿已展示给用户并取得**一次明确确认**。
2. 用户明确授权使用其形象/声音生成商业视频。
3. 档案 `presence` 模块中已记录形象偏好。

任一未满足 → 停在脚本阶段，不要发起生成。

## HeyGen API 速查

| 项 | 值 |
|---|---|
| Base | `https://api.heygen.com` |
| 创建视频 | `POST /v2/video/generate` |
| 查询状态 | `GET /v2/video/{video_id}` |
| 鉴权头 | `X-Api-Key: $HEYGEN_API_KEY` |
| Key 来源 | **仅**环境变量 `HEYGEN_API_KEY` |

### v2 请求体核心字段

```json
{
  "video_inputs": [
    {
      "character": {
        "type": "avatar",
        "avatar_id": "<AVATAR_ID>",
        "avatar_style": "normal",
        "voice": {
          "type": "audio",
          "input_text": "<完整逐字稿>",
          "voice_id": "<VOICE_ID>",
          "speed": 1.0
        }
      },
      "background": {
        "type": "color",
        "value": "#FFFFFF"
      }
    }
  ],
  "dimension": {
    "width": 1080,
    "height": 1920
  },
  "language": "zh",
  "caption": false
}
```

要点：
- `input_text` 是一整段文本，HeyGen 负责切分；把分镜的句子用空格或换行连接，**不要**手动加时间戳。
- 竖屏 `1080x1920`；横屏 `1920x1080`（B站/LinkedIn 用）。
- `language` 用 `zh` 或 `en`。
- `speed` 默认 1.0；语速偏慢可调 1.05，不要超过 1.15（会失真）。
- 字幕需要自己烧录时，设 `caption: true` 会生成带字幕版本。

### 形象与音色选择
- `avatar_id` 从 HeyGen 控制台 **Studio → Avatars** 取；本 Skill 不内置形象列表。
- 形象匹配原则：**生活化 > 商务精英**。选一个看起来会干活的人。
- `voice_id` 从 **Studio → Voices** 取；中文选自然度高的，避开播音腔。
- 建议用户到 HeyGen 免费额度里先试 2~3 个形象再定。

## 执行流程

### 1. 前置检查
```bash
python3 <skill-path>/scripts/pv-check.py --dossier pinned-dossier.md --stage pre-generate
```
检查档案完整性、字数、结构、无编造风险项。

### 2. 生成
```bash
python3 <skill-path>/scripts/pv-generate.py \
  --dossier pinned-dossier.md \
  --script scripts/final-script.txt \
  --avatar-id <AVATAR_ID> \
  --voice-id <VOICE_ID> \
  --output out/pinned-video.mp4
```
脚本会自动轮询直到视频就绪并下载到 `--output`。
`--dry-run` 只打印请求体不调用 API。

### 3. 交付
报告：
- 视频文件路径
- 时长与分辨率
- 用了哪个形象 / 音色
- 建议先看哪几处（通常是最容易假的地方：开头 3 秒、手部特写、结尾 CTA）

## 失败处理

| 现象 | 处理 |
|---|---|
| 401 | `HEYGEN_API_KEY` 未设或过期 → 让用户去 HeyGen 控制台取新 Key |
| 配额不足 | 提示用户充值，或改用免费形象/缩短重试 |
| 状态卡在 `processing` 超时 | 视频较大时正常；延长轮询或稍后再取 |
| 成片「不像人」 | 走 `task-quality.md` 迭代：换形象、调速、拆句重生成 |

## 边界
- **API Key 绝不写入**档案、脚本输出、仓库文件或对话回执。
- 未经用户明确授权，不使用其形象生成商业视频。
- 不代用户发布到任何平台。
