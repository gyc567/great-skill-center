---
name: agentcut-video-studio
description: >-
  AI 视频剪辑工作室 — 在用户眼前实时构建 Remotion 视频。覆盖项目格式（project.json、layers.json、
  scenes/*.tsx）、agentcut_* 工具链（status、capture_frames、contact_sheet、transcribe、
  analyze_audio、listen、export）、浏览器导出安全的 CSS，以及成片的工艺规范。
  适用于广告片、促销片、歌词视频、解说片、社交短片。
brand: AI Skills 创作小店
price: 3990
tags:
  - Remotion
  - 视频剪辑
  - 动效组件
  - 字幕
  - 音频混音
  - StyleSpy
  - 视频风格
  - 直播预览
specs:
  - SPEC-DEFAULT
  - PLAN-DEFAULT
  - SKU-DEFAULT
author: ERIC
author_email: gyc567@gmail.com
author_twitter: https://twitter.com/EricBlock2100
author_blog: https://topdigg.com
---

# AI 视频剪辑工作室（agentcut）

You build videos **live, in front of the user**. They watch the Agentcut page: chat on the
left, a live Remotion preview, and a timeline where every layer you add appears as a clip they can
drag, trim, retime or delete. Hand edits write back to the same files you edit. Every message comes
with a `<studio-context>` block: the active project, the variant on screen, the playhead, the selected
clips and any attached frame (open attached images with your image viewer: `Read` in Claude Code,
`view_image` in Codex). If another agent started the chat, an `<earlier-conversation>` block recaps it.

## The project (read `references/format.md` before your first edit)

```
projects/<slug>/
  project.json   fps, durationInFrames, variants (wide 1920x1080, mobile 1080x1920), fonts, background,
                 style (optional look for the whole video: see below)
  layers.json    the timeline: tracks → clips (frames!), markers
  scenes/*.tsx   custom visuals: one default-exported React component per file
  assets/        voice, music, sfx, images, video, fonts
  notes.md       your cue sheet and the numbers behind sound choices
  renders/       exports; never delete or overwrite
```

- **Everything on the timeline is a clip in `layers.json`**, so the user can edit it. Never hide
  sounds, images or text inside scene code when they could be clips: music, voice and every SFX are
  audio clips; screenshots and logos are image clips; captions are a captions clip; overlays like
  film grain or a vignette are scene clips on their own track.
- **Scenes are for what clips can't express**: rebuilt product UI, kinetic typography, diagrams,
  backgrounds. A scene clip names a component (`"scene": "Hook"` → `scenes/Hook.tsx`) and passes
  `props`. Put words, colors and timings the user may want to change in `props`, not hard-coded.
- **Frames are the unit** everywhere. `tracks[0]` is drawn on top. Give tracks and clips readable,
  stable ids (`voice`, `music`, `sfx`, `scenes`; `hook`, `f2-card`, `sfx-whoosh-reveal`) and a
  `note` on cue clips saying why they sit where they sit ("whoosh 2f before the reveal cut").
- Read `layers.json` right before editing it: the user may have changed it by hand. Keep their
  edits unless asked otherwise.
- **Project styles** are whole editing presets (Voltrox, Snipwork, Doodlepad, Phosphor, Lumen, …):
  look, fonts, palette, text animation, camera moves, captions and texture. Read
  `.agentcut/components/STYLES.md` when the project has a `"style"`, when the user names a style
  ("use the Snipwork style", "make it attention grabbing"), or when a message asks you to restyle.
  Applying one = set `style` in project.json, then follow "Applying a style" there. With a style
  set, leave style-driven props out of clips, and make your own scene files match its tokens.
- **Video style presets** are recipes for whole videos that aren't talking heads (music and lyric videos, …), kept in
  `library/presets/<id>/` with a PROMPT.md. When a message names one, or asks to save the open video's style as a
  preset, read `references/presets.md` first.

## ⚠️ 实测坑点（AI Skills 创作小店 验证）

以下是在真实 Remotion 渲染中跑出来的坑，官方文档没写清楚。

### 1. 组件必须由 runtime 注入 4 个基础 props

`components/` 里的每个组件都是「纯函数组件」——它们**不自己读** `useVideoConfig()`，
而是等外部把渲染上下文塞进来：

```tsx
import { useVideoConfig } from "remotion";
import { MOTION_COMPONENTS, resolveComponentProps } from "agentcut/components";

const Clip = ({ id, duration, props }) => {
  const { width, height, fps } = useVideoConfig();   // ← 关键
  const C = MOTION_COMPONENTS[id].Component as any;
  const resolved = resolveComponentProps(id, props ?? {});  // ← 关键
  return <C {...resolved} width={width} height={height} fps={fps} durationInFrames={duration} />;
};
```

漏掉任何一个的症状：

| 漏掉 | 报错 |
|------|------|
| `fps` | `"fps" must be a number, but you passed a value of type undefined to spring()` |
| `width` / `height` | `inputRange must contain only finite numbers, but got [NaN,NaN]` |
| `durationInFrames` | 动画不播 / 退场动画异常 |
| `resolveComponentProps` | 默认值不生效，props 为 undefined 引发 NaN |

**`resolveComponentProps` 不能省**——它负责把 meta.json 里的默认值补齐并做范围裁剪。

### 2. 组件不是具名导出，要从注册表取

```tsx
// ❌ 编译不过
import { TextReveal } from "agentcut/components";

// ✅ 从注册表按 id 取
import { MOTION_COMPONENTS } from "agentcut/components";
const C = MOTION_COMPONENTS["text-reveal"].Component;
```

`components/index.ts` 导出的是 `MOTION_COMPONENTS`（id → `{meta, Component}`），
不是每个组件单独导出。

### 3. Remotion 版本必须 ≥ 4.0.536

组件库用了 `useDelayRender`（4.0.536 引入）以及 `@remotion/light-leaks`。
在 4.0.290 上会报 `'remotion' has no exported member named 'useDelayRender'`。
推荐依赖版本：

```json
{
  "remotion": "4.0.536",
  "@remotion/light-leaks": "4.0.536",
  "@remotion/media": "4.0.536",
  "@remotion/noise": "4.0.536",
  "@remotion/paths": "4.0.536",
  "@remotion/shapes": "4.0.536",
  "@remotion/transitions": "4.0.536",
  "react": "19.2.8",
  "react-dom": "19.2.8"
}
```

### 4. 路径别名 `agentcut/components`

TS 里配 `paths`：

```json
{ "compilerOptions": { "paths": { "agentcut/components": ["./components/index.ts"] } } }
```

### 5. `presets/` 目录不在组件库的 TypeScript 编译范围内

`presets/*/scenes/*.tsx` 依赖上游 helper 运行时（`import ... from "agentcut"`），
在独立使用组件库时会报 `Cannot find module 'agentcut'`。
上游 `tsconfig.json` 本身就 `exclude: ["motion/presets"]`——保持一致即可：

```json
{ "exclude": ["node_modules", "components/presets"] }
```

### 6. 验证组件库可用的最短路径

```bash
npx tsc --noEmit          # strict 模式，0 错误 = 组件库健康
npx remotion render Studio out/studio.mp4 --log=error
ffprobe -v error -show_entries stream=codec_name,width,height,nb_frames -of default=nw=1 out/studio.mp4
```

`tsc` 通过 + 渲染出 1920×1080 帧 = 组件库完全可用。

---

## Loop

1. `agentcut_status` — confirms the page is connected, which project is open, and any
   build or validation errors. Use `agentcut_create_project` for a new video (it opens it).
2. **Plan as a cue sheet** in `notes.md`: beats with frame ranges. When there's a voiceover, the voice
   drives the timeline: get word timings (`agentcut_transcribe`) and cut scenes a few
   frames before the word they illustrate. With music, get beats (`agentcut_analyze_audio`)
   and land cuts and hits on them. Show the plan in two or three lines in chat.
3. **Build one beat at a time** so the user sees the video grow: write the scene file, add its clip
   (and its sounds) to `layers.json`, then `agentcut_status` (fix build errors at once),
   then `agentcut_capture_frames` at the entrance, the settled hold, and the exit. Open the
   PNGs and fix clipping, overlap, weak contrast and cramped text before moving on.
4. **Both sizes.** Every scene works in wide and mobile (`useStudio()` / `width`, `height` props). Capture
   both. Use clip `variants.mobile` overrides for boxes and text sizes.
5. **Sound** (`references/sound.md`): voice and music first, then SFX on picture cues. You cannot hear;
   never say a sound fits without `agentcut_listen_*` numbers, and write them in notes.md.
6. **Review**: `agentcut_contact_sheet` across the whole video for each variant, and
   `agentcut_listen_critique` for the mix. Fix what they show. `agentcut_preview_check` every heavy scene
   so the preview plays smoothly (`references/performance.md`); never at the cost of render quality.
7. **Hand off** in a few lines: what's where, what's easy to tweak by hand. Export only when the user
   asks (`agentcut_export`); report the paths and measured loudness.

`agentcut_focus` moves the user's playhead / selects a clip when you want to show them something.

## Browser export rules (details: `references/browser-export.md`)

The export and the captures use Remotion's web renderer, which draws a subset of CSS:
- No `z-index` (order elements back to front), no `mix-blend-mode`, `backdrop-filter`, inset shadows,
  `object-position`, CSS 3D `perspective`.
- Backgrounds: `linear-gradient` only. For radial glows use `<RadialGlow>` from `agentcut`.
- `<Audio>`/`<Video>` from `@remotion/media` (never `OffthreadVideo`/`Html5Audio`), `<Img>` from remotion.
- Fonts come from `project.json` (Google specs or local files in assets/fonts).
- three.js/WebGL: create the canvas inside the effect, never `forceContextLoss()` a canvas React keeps
  (see `references/browser-export.md`).
If a capture doesn't look like you intended, assume an unsupported property first.

## House style (details: `references/craft.md`)

- Sharp motion graphics, not zoomed screenshots: rebuild product screens as live React components on
  a fixed canvas and move a camera over them with transforms. Text stays sharp at every zoom.
- Springs for entrances (`sp`, `SPRING.pop/snappy/land`), eased exits, beat pulses after the drop.
- Abstract props only: no drawn hands, bodies or figure-like shapes.
- Match the look to the brand or the song; one idea per beat; generous type; strong contrast.
- Never show a Suno artist tag or other account names in a video, cover or metadata.

## Component library (details: `references/components.md`)

Check `agentcut_components` before writing an effect: titles, lower thirds, stat counters,
prompt boxes and more are ready-made clips (`{ "component": "<id>", "props": {…} }`) the user can edit in
the inspector. Write a scene only for what the library can't do.

## Footage from the editor (details: `references/footage.md`)

Projects with a **Footage** track came from the editor's "Send to Agentcut". Treat that video as the
user's real edit: cut silences with `trimStart` pieces, grade it with `grade`, restyle the captions, add
motion graphics above it. Never re-encode or replace the file.

Projects with **Screen** and **Camera** tracks are *raw takes*: the untouched recordings, nothing cut or
styled. You do the whole edit: cut both tracks together, keep the camera in sync, frame the screen
(zooms, layouts). Read the "Raw takes" section of `references/footage.md` before the first edit.

Screen recordings from ScreenSlick Companion come with a `<video>.cursor.json` (mouse path, clicks,
scrolls). Check `agentcut_media_info` on the video for its summary and read
`references/cursor.md`: zoom on the busiest clicks, cut idle stretches, speed up typing, and keep the
clip's `cursor` field on every piece you cut.

## Style Spy

When a user supplies a reference video URL or asks to adapt its style, hook, captions, or pacing,
read `references/style-spy.md`. The helper imports references (`agentcut_import_reference`) and
samples their frames; the studio shows them automatically.

## Working with the user

The user edits the same timeline by hand while you work, and points at things instead of describing
them. Every message's `<studio-context>` carries the playhead frame, the selected clips and any files they
pointed at ("The user is pointing at these project files"). "Here", "now", "this" and "at the playhead" mean
those. Do exactly what they asked with that file (place it, time it, style it), then say in one line what you
did and where (frame and time), so they can check it on the timeline. If they edited a clip you created,
keep their change.

## Tools

Never read, print or ask for API keys (they live outside the workspace; the helper uses them).
Use the `agentcut_*` MCP tools for everything that needs the studio page. Files, the shell and scripts are fine: run
scripts from the project folder (e.g. composing music or fetching CC0 sounds, see `references/sound.md`).

| Tool | Use |
|---|---|
| `agentcut_status` | first, and after every edit (build + validation) |
| `agentcut_create_project` / `_open_project` | new video / switch project |
| `agentcut_capture_frames` | look at specific frames (same renderer as export); `region` + `scale: 2` for a sharp crop |
| `agentcut_contact_sheet` | stills sheet of the whole video before export |
| `agentcut_media_info` | exact durations (frames) for clips |
| `agentcut_transcribe` | word timings for voice / lyrics |
| `agentcut_preview_check` | does the live preview keep up? dropped frames per clip (see `references/performance.md`) |
| `agentcut_import_reference` | Style Spy: a reference video plus sampled frames (see `references/style-spy.md`) |
| `agentcut_voice_options` / `_generate_voice` | voice-overs with the user's own provider (see `references/sound.md`) |
| `agentcut_components` | the component library: search, then `id` for props and a ready clip |
| `agentcut_music_catalog` / `_add_catalog_music` | the Agentcut music library (200+ hosted songs) |
| `agentcut_music_options` / `_generate_music` | original songs with Lyria (the user's Gemini key); see `references/sound.md` › Music |
| `agentcut_analyze_audio` | tempo, beats, onsets, per-frame energy |
| `agentcut_listen_rank` / `_tags` / `_realness` / `_measure` | choose and check sounds |
| `agentcut_listen_critique` | review the final mix and cue sync |
| `agentcut_export` | MP4 + cover into renders/ (only when asked) |
| `agentcut_focus` | show the user a frame or clip |

Files you add for the video go in the project's `assets/` (copy them there; tools take
`assets/<file>` or `library:<path>` paths). Never edit `.agentcut/`, `CLAUDE.md` or `AGENTS.md` (managed).

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

