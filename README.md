# BoBee Publisher

> 端到端公众号长文配图发布技能 — BoBee 蜜蜂打工人 AI 插画 + Guizang Editorial 杂志排版

## 这是什么

一键完成三件事：
1. **分析文章** — 提取认知锚点，设计配图策略
2. **生成 BoBee 插画** — 调用 RunningHub API 生成暖调手绘蜜蜂打工人配图
3. **排版发布** — 生成微信封面对 + 小红书社交卡组

## 快速开始

### 安装

将本目录放入 WorkBuddy 的 skills 目录：

```bash
cp -r bobee-publisher ~/.workbuddy/skills/
```

### 配置

```bash
export RUNNINGHUB_API_KEY="你的RunningHub API Key"
```

### 使用

在 WorkBuddy 中：
```
帮我把这篇文章用 BoBee 配图排版成公众号
```

## 技能结构

```
bobee-publisher/
├── SKILL.md                           # 技能定义 + 完整工作流
├── scripts/
│   └── generate.py                    # RunningHub 生图脚本（4个模型）
├── references/
│   ├── bobee-ip.md                    # BoBee IP 定义 + Prompt 片段
│   ├── illustration-workflow.md       # 配图策略 + 8种结构
│   └── api-docs.md                    # API 配置参考
└── assets/
    └── templates/
        └── template-editorial-card.html  # Guizang Editorial 排版模板
```

## 输出示例

| 规格 | 尺寸 | 用途 |
|------|------|------|
| 公众号主封面 | 2100×900 (21:9) | 微信推文封面 |
| 公众号方封面 | 1080×1080 (1:1) | 转发小卡片 |
| 社交卡 | 1080×1440 (3:4) | 小红书/朋友圈 |

## BoBee IP

BoBee 是一只暖黄色蜜蜂打工人：大头小身体、六边形眼镜、挂着"BoBee"工牌、在怪诞职场场景里认真干活的 IP 角色。

## 依赖

- Python 3.9+
- RunningHub API Key
- Playwright CLI（用于渲染 HTML → PNG）
- Google Fonts（Noto Serif SC、Inter、IBM Plex Mono，排版用）

## License

MIT
