# Anatomy（等距机器插图）

> **用一个真实存在的机器来讲清楚一个概念。**
> 不是画方框加箭头 —— 造一台会动的小仪器，让读者认出它。
> 品牌化改造：AI Skills 创作小店

[![许可](https://img.shields.io/badge/许可-MIT-blue)](https://opensource.org/licenses/MIT)
[![Node](https://img.shields.io/badge/Node-%E2%89%A5%2020.10-green)](https://nodejs.org/)
[![依赖](https://img.shields.io/badge/依赖-0-green)]()
[![品牌](https://img.shields.io/badge/品牌-AI%20Skills%20创作小店-pink)](https://github.com/gyc567/great-skill-center)

---

## 💡 核心理念

> **物体就是解释。**

| 概念 | 造出来的机器 |
|------|-------------|
| 一个 GPU context 服务多个 canvas | **龙门绘图机**：一个打印头巡游 16 个孔位 |
| 缓存键命中就不重算 | **弹子锁**：每个弹子都对上，锁芯才转 |
| 7 个渲染目标、每像素字节数不同 | **七个抽屉的柜子**：每个抽屉的深度就是它的字节数 |
| 可分离模糊（49×49 vs 49+49） | **钢钉床**与两把梳子并排放在导轨上 |
| 弹簧压紧并倾斜 | **测试台**：弹簧、探针、量表 |
| 高度剖面 | **轮廓规**：贴着边缘压出的形状 |
| 面向决定亮度 | **小型摄影棚**：转台四周的主光与补光 |

---

## 🎨 它产出什么

- **多部件精确实体**：底座在脚上、导轨带刻度、滑座带衬套、滚花旋钮、线圈弹簧、带指针的量表、螺丝是点点
- **四色分层明暗** + **正确画家顺序**（后画的在上）
- **带框卡片**：标题、提示、实时读数
- **平缓缓动的动效**
- **数字全部来自驱动部件的同一个模型** —— 不会说谎
- 可选 **WebGL 着色器**（火焰、尾焰、水波、焦散、灯光）嵌在同一个等距视角里

---

## 🚀 快速开始

```bash
# 1. Node 依赖（无 package.json，按 CI 的方式装到独立目录）
npm install --prefix /tmp/anat-deps --no-audit --no-fund --ignore-scripts \
  react@19.3.0 react-dom@19.3.0 typescript@5.9.3 esbuild@0.28.2

# 2. 构建示例
export NODE_PATH=/tmp/anat-deps/node_modules
node examples/dial-indicator/build.mjs          # 暗色
node examples/dial-indicator/build.mjs --light  # 亮色

# 3. 跑测试
node --test scripts/*.test.mjs
```

---

## 📚 八个完整示例

| 示例 | 是什么 | 规模 |
|------|--------|------|
| `dial-indicator/` | 表盘量表 + 支架 | 最小，约 300 行 |
| `desk-computer/` | 桌面电脑，可打字的键盘，CRT 画面 | 85 实体 / 850 路径 |
| `arcade-cabinet/` | 竖立街机，拆侧板 | 约 240 实体 / 15 根线缆 |
| `ripple-tank/` | 学校波纹槽，44° 俯视 | 238 图层 |
| `raptor-engine/` | 挂在试验架上的火箭发动机 | 11 个组件 + WebGL 尾焰 |
| `test-rig/` | 真实产线图：玻璃按钮 + 探针 + 量表 | 53 实体 / 470 路径 |
| `spot-plate/` | 六对玻璃滴在点滴板上 | 深度排序合成 |
| `turning-dial/` | 3D 模式：密码转盘 + 机械手 | 约 90 活体部件 |

> **质量标尺**：`test-rig` 是绘图质量的标尺，`raptor-engine` 是着色器工作的标尺。

---

## ✅ 交付实测

| 项 | 结果 |
|----|------|
| **测试套件** | ✅ **279/279 全部通过**（`node --test scripts/*.test.mjs`） |
| `dial-indicator` 构建 | ✅ 0.2s，产出 136 KB HTML |
| `desk-computer` 构建 | ✅ 0.2s |
| `arcade-cabinet` 构建 | ✅ 26.6s，984 KB，349 项，15 线缆 |
| `ripple-tank` 构建 | ✅ 1.1s，494 KB，238 图层 |
| `turning-dial` 构建 | ✅ 21.5s，658 KB，88 部件 |
| `raptor-engine` 构建 | ⏳ 最复杂，需 >4 分钟（CI 超时设为 30 分钟） |
| Node 版本 | ✅ v22.22.0（需 ≥ 20.10） |

---

## 🔧 依赖

| 依赖 | 必需性 | 说明 |
|------|--------|------|
| **Node ≥ 20.10** | ✅ 必需 | 构建脚本 |
| **react / react-dom** | ⚠️ 仅 React 示例 | `test-rig` / `spot-plate` |
| **typescript / esbuild** | ⚠️ 仅 React 示例 | 同上 |
| **Chrome / Chromium** | ⚠️ 仅自检 | 官方 CI 才装 |

> 框架无关的示例（`dial-indicator` / `desk-computer` / `arcade-cabinet` / `ripple-tank` / `turning-dial` / `raptor-engine`）**不需要任何 npm 依赖**，只需 Node。

---

## 📄 许可与来源

**MIT**。原样收录自 [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) by Ryan，
上游 commit `e948829`，未做任何修改，其自身 LICENSE 保留在目录内。

> 本 Skill 是 `charles-video-maker` 内嵌 `anatomy/` 的独立发行版本，
> 便于单独用于「文档插图 / 博客配图 / 落地页原理图」等**不涉及视频**的场景。

Copyright (c) Ryan (@wheresryan22)

---

## 📞 定制化开发

如需**定制化开发**，可直接联系 ERIC：

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
- 上游 Skill：`charles-video-maker`（把 Anatomy 的机器渲成视频）
