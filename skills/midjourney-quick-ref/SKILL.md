---
name: midjourney-quick-ref
brand: AI Skills 创作小店
description: "99个MJ常用指令速查卡，覆盖风格/参数/比例/版本，图文对照，设计师必备引流款。¥0.99"
priceConfigJson: {"billingCycleType": "buyout", "amount": 99, "currency": "CNY", "payType": "PREPAY"}
---

# Midjourney 速查卡

> 99个最常用指令，即查即用

## 基础参数

| 参数 | 用法 | 示例 |
|------|------|------|
| `--ar 16:9` | 画面比例 | `--ar 16:9` 横屏 |
| `--ar 9:16` | 竖屏比例 | `--ar 9:16` 故事流 |
| `--ar 1:1` | 方形 | `--ar 1:1` 头像 |
| `--v 6` | 版本 | `--v 6` 第六代模型 |
| `--niji 6` | 动漫风格 | `--niji 6` 日系插画 |
| `--s 250` | 风格化 | `--s 750` 高风格化 |
| `--q 1` | 质量 | `--q 0.5` 草稿 |
| `--seed` | 随机种子 | 锁定风格 |
| `--tile` | 平铺 | `--tile` 图案 |
| `--pan` | 扩展 | `--pan` 向外扩展 |
| `--zoom 2x` | 缩放 | `--zoom 2x` 放大2倍 |

## 常用指令前缀

```
/imagine prompt: [主体描述], [风格], [光效], [构图], [参数]
```

## 风格关键词

### 摄影风格
- `portrait photography, f/1.8, studio lighting`
- `landscape photography, golden hour, 35mm`
- `street photography, film grain, Leica`

### 插画风格
- `watercolor illustration, soft colors`
- `vector art, flat design, minimal`
- `ink illustration, traditional Chinese style`

### 3D风格
- `3D render, octane, unreal engine`
- `isometric, low poly, soft shadows`
- `blender, ray tracing, 4K`

## 常用主体词

| 场景 | 关键词 |
|------|--------|
| 人物 | `beautiful woman, 25yo, detailed eyes, natural lighting` |
| 产品 | `product photography, white background, studio lighting` |
| 建筑 | `modern architecture, concrete, glass, golden hour` |
| 食物 | `food photography, top-down, natural light, 4K` |
| 头像 | `professional portrait, solid background, Retouched` |

## 负面提示词
```
--no blur, noise, low quality, distorted, watermark, text
```

## 版本差异速查

| 版本 | 擅长 | 适合 |
|------|------|------|
| V6 | 照片级真实感 | 产品/人物 |
| Niji6 | 动漫/日式 | IP/插画 |
| V5.2 | 艺术风格 | 概念/海报 |
| V4 | 通用稳定 | 日常使用 |

## 常用组合公式

```
主体 + 光效 + 风格 + 比例 + 版本
```

例：`a cat on a windowsill, golden hour, watercolor, --ar 16:9 --v 6`
