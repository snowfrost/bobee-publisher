---
name: bobee-publisher
description: "端到端公众号长文配图发布技能。组合 BoBee 蜜蜂打工人 IP 插图生成与 Guizang Editorial 杂志排版，将 IMA 文章、公众号链接、Markdown/Notion 文档转化为配图精美、排版完整的公众号内容包。触发词包括：公众号配图、文章插图、BoBee配图、公众号排版、文章封面、图文排版、bobee、蜜蜂配图、社交卡、social card、微信封面。当用户要求为一篇中文文章生成配图加排版、做成公众号、画插画然后排版发布时使用。"
agent_created: true
---

# BoBee Publisher — 公众号配图发布技能

## 概述

一站式完成三件事：**分析文章 → 生成 BoBee 插画 → 排版成公众号封面+社交卡**。

默认 IP 是 BoBee（蜜蜂打工人）：暖黄色圆头小身体、六边形眼镜、挂着"BoBee"工牌、在怪诞场景里认真干活的职场蜜蜂。详见 `references/bobee-ip.md`。

所有图片默认 16:9 横版、暖调手绘涂鸦风、纯白背景。

---

## 前置条件

首次使用需设置 API Key：

```bash
export RUNNINGHUB_API_KEY="你的32位API Key"
```

从 [RunningHub 控制台](https://www.runninghub.cn) 获取。

---

## 核心工作流

### 第一步：读取文章

从用户提供的 IMA 文章、公众号链接、Markdown 文件或截图提取全文。

提炼：
- 核心观点与认知转折
- 适合配图的"认知锚点"段落
- 哪些地方只需要文字不需要图

### 第二步：设计 Shot List

按照 `references/illustration-workflow.md` 中的 8 种结构类型，为每个认知锚点设计一张配图。

每张图写清：
- 放在哪个段落后
- 核心意思
- 结构类型（工作流/系统局部/前后对比/角色状态/概念隐喻/方法分层/地图路线/小漫画分镜）
- BoBee 在图里做什么
- 建议元素 + 中文标注词

默认 4-8 张。文章很短时 1-3 张。

### 第三步：逐张生成 BoBee 插画

使用 `scripts/generate.py` 逐张生成。

**Prompt 构建规则：**
- 读取 `references/bobee-ip.md` 获取 BoBee 外形描述
- 按照 `references/illustration-workflow.md` 中的 Prompt 模板构建
- 必含：BoBee 外形（大头、六边形眼镜、BoBee工牌、暖黄条纹身体）、纯白背景、暖调手绘、16:9
- 每张图只讲一个核心结构
- 每次发明新隐喻，不复刻旧构图

**生成命令：**

```bash
# 默认（最便宜）
python scripts/generate.py "<英文prompt>" -o output.png

# 高质量（推荐用于最终发布）
python scripts/generate.py "<prompt>" --model gpt-image2 --res 2k --ratio 16:9 -o output.png

# 使用参考图引导
python scripts/generate.py "<prompt>" --model gpt-image2 --res 2k --ratio 16:9 --image-file reference.png -o output.png
```

API 详情见 `references/api-docs.md`。

**生成后检查：**
- BoBee 的六边形眼镜、"BoBee"工牌、大头比例是否到位
- 背景是否纯白
- 画面是否太满/太像PPT/太幼稚
- 中文标注是否少、短、能读

### 第四步：排版成公众号封面 + 社交卡

使用 Guizang Editorial Magazine × E-ink 风格排版。

**产出物：**

| 规格 | 用途 |
|------|------|
| 21:9 (2100×900) | 公众号主封面 |
| 1:1 (1080×1080) | 公众号方封面 |
| 3:4 (1080×1440) × N | 社交卡组（小红书/朋友圈） |

**排版步骤：**

1. 创建任务目录 `social-card-<slug>/`
2. 把生成的 BoBee 插画复制到 `assets/`
3. 复制 `assets/templates/template-editorial-card.html` 为 `index.html`
4. 用 `ink-classic` 主题（暖纸墨色）：`<html data-theme="ink-classic">`
5. 按页面计划构建 poster 内容：
   - `poster.wide` — 21:9 封面（标题 + BoBee 视觉证据）
   - `poster.square` — 1:1 方封面（短标题、大字、无图）
   - `poster.xhs` × N — 3:4 社交卡（一页一图一文）
6. 启动本地 HTTP 服务器：`python -m http.server 8899`
7. 用 Playwright 渲染每张 `.poster` 和 `.cover` 为 PNG
8. 保存到 `output/`

**21:9 封面排版要点：**
- 标题在左（大号 serif），BoBee 插图在右
- 底部 issue strip：分类/主题/关键词
- 标题字体：`h-display` 96-128px

**1:1 方封面排版要点：**
- 短标题（4-10字），提炼自长标题
- 大字居中，无图（除非用户要求）
- 足够的呼吸感

**3:4 社交卡排版要点：**
- 每页一个 idea
- BoBee 插图 + 简短文案 + 引语/清单
- 内容覆盖 ≥75% 画布高度
- 使用 `.frame-img` 容器装插图

**渲染命令（Playwright）：**
```bash
playwright-cli open http://localhost:8899/index.html --browser=msedge
playwright-cli screenshot "#wechat-21x9" --filename=output/wechat-21x9-cover.png
playwright-cli screenshot "#wechat-1x1" --filename=output/wechat-1x1-cover.png
playwright-cli screenshot "#xhs-01" --filename=output/xhs-01.png
# ... 依此类推
playwright-cli close
```

### 第五步：交付

交付物包括：
- 所有 BoBee 插画原图
- 微信封面对（21:9 + 1:1）
- 社交卡组（3:4 × N）
- HTML 源文件（可二次修改）

---

## 快速参考

### BoBee Prompt 核心片段

```
BoBee bee worker with large round cute head (head-to-body about 1:1, big-head proportion),
slightly chubby small body, warm bright yellow body, dark brown horizontal stripes,
hexagonal glasses (key identifier), small pink blush on cheeks, translucent light blue wings,
two small antennae, blue lanyard with white badge reading "BoBee".
Hand-drawn doodle, warm palette, clean white background, whimsical workplace humor.
```

### 常用命令速查

```bash
# 生图
python scripts/generate.py "<prompt>" --model gpt-image2 --res 2k -o output.png

# 排版
cp assets/templates/template-editorial-card.html social-card-xxx/index.html
# 在 index.html 中构建 poster 内容
python -m http.server 8899 &
playwright-cli open http://localhost:8899/index.html --browser=msedge
playwright-cli screenshot "#wechat-21x9" --filename=output/cover.png
playwright-cli close
```

---

## 资源清单

| 类型 | 文件 | 用途 |
|------|------|------|
| 脚本 | `scripts/generate.py` | RunningHub API 生图 |
| 参考 | `references/bobee-ip.md` | BoBee IP 定义 + Prompt 片段 |
| 参考 | `references/illustration-workflow.md` | 配图策略 + 8 种结构类型 |
| 参考 | `references/api-docs.md` | API 配置 + 模型列表 |
| 模板 | `assets/templates/template-editorial-card.html` | Guizang Editorial 杂志排版模板 |
