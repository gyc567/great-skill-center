# Craft: how the owner's videos are made

The reference library is the owner's hand-made Remotion studio (`video-studio`). New Studio videos should
match it. What makes those videos work:

## Structure

- **One idea per beat**, 2–6 s each. A 60 s launch spot has ~10 beats: pain → reveal → 3–6 feature beats →
  proof/flow → end card (logo, URL, "now live").
- **The voice drives the cuts.** Every scene starts a few frames (≈ 8 f at 30 fps) before the word it
  illustrates; on-screen elements pop on their keyword's start frame. Keep a word-index cue table in
  notes.md (`reveal = word "meet" − 8f`). With no voice, the music's beats and sections drive it.
- **Music has a shape**: quiet intro under the hook, a drop on the reveal, a final chord on the end card.
  Put markers on the drop and the final hit; cut and flash on them.
- **Wide and mobile are designed, not cropped**: both at 1080 px on the short side. Stack horizontally in
  wide, vertically in mobile; bigger type in mobile; keep important content out of the bottom 18% and top
  10% of mobile (platform UI).

## Motion

- Entrances: springs. `pop` (scale 0.6→1 + rise + fade over ~5 f), `rise` (fade + 30 px rise), `land` for
  heavy titles. Stagger lists by 3–6 frames.
- Exits: short eased fades with a slight scale-down / rise and blur (≈ 7 frames), overlapping the next
  scene's entrance.
- After the drop, a **beat pulse** (0..1 decaying over ~8 f on each beat) drives subtle scale/brightness of
  backgrounds and accents — never the text you need to read.
- Flashes: brief white overlay (opacity ≤ 0.35, ~10 f) on the drop and the final hit only.
- Camera moves over rebuilt UI: ease in/out between framings, hold long enough to read (≥ 1.2 s per line of
  text the viewer must read).

## Visuals

- **Rebuild product UI as live components** (real layout, labels, brand colors) on a fixed canvas, and move a
  camera (scale/translate) over it. Never zoom into screenshots: they blur.
- Brand palette in one constant object; one gradient for accents; dark backgrounds with radial glows
  (`RadialGlow`) for depth.
- Generous type: titles 110–150 px wide / 120–170 px mobile at 1080 short side; body ≥ 40 px.
- Icons as inline SVG strokes (24×24 viewBox, round caps), not emoji.
- Abstract props only: no drawn hands, bodies or figure-like shapes.
- Lyric videos: one phrase per layout, accent words highlighted, kicker words smaller; the look follows the
  genre (night-station LED, xerox art-punk, pastel line diagrams, tattoo flash…).

## Captions

Word-by-word for talking-head and voice-driven pieces: 2–4 words per line, the active word highlighted,
lines break at pauses. Check fast passages by capture; Whisper can merge or drop words.

## Before calling it done

- Contact sheet of each variant: no clipped text, no empty frames between scenes, consistent margins.
- `agentcut_listen_critique`: loudness near −14 LUFS after export normalization, voice clearly above
  music, every SFX on its cue.
- notes.md updated: cue sheet, sound choices with their numbers, anything the user should know.

<!-- ERIC-AUTHOR-INFO:START -->
---

## 📬 作者信息

**ERIC** — AI技术专家，专注于人工智能和自动化工具的研究与应用

| 渠道 | 链接 |
|------|------|
| 📧 邮箱 | [gyc567@gmail.com](mailto:gyc567@gmail.com) |
| 🐦 Twitter | [@EricBlock2100](https://twitter.com/EricBlock2100) |
| 💬 微信 | `360369487` |
| ✈️ Telegram | [@fatoshi_block](https://t.me/fatoshi_block) |
| 📢 Telegram 频道 | [@cryptochanneleric](https://t.me/cryptochanneleric) |
| 🔐 加密情报 TG 群 | [@btcgogopen](https://t.me/btcgogopen) |
| ▶️ YouTube | [@0XBitFinance](https://www.youtube.com/@0XBitFinance) |
| 🌐 个人技术博客 | [topdigg.com](https://topdigg.com) |

> 本 Skill 由 ERIC 免费提供。想深入交流或获取更多同类 Skill，欢迎通过上表任一渠道联系。

<!-- ERIC-AUTHOR-INFO:END -->

