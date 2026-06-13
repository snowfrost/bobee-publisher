# 文章配图策略模板

## 工作流

### 1. 消化文章
- 读完文章，提炼核心观点、认知转折点、关键段落
- 找到适合用图解释的"认知锚点"
- 不要平均配图，优先选择：核心判断、断点、闭环、对比、隐喻、路径、状态变化

### 2. 设计 Shot List
每张图需要明确：
- 放在哪个段落后
- 图的核心意思
- 结构类型（从8种中选1种）
- BoBee 在图里的动作
- 建议元素 + 中文标注词

默认 4-8 张，文章很短时 1-3 张。

### 3. 8种结构类型

| # | 类型 | 适合场景 | 构图 |
|---|------|---------|------|
| 1 | 工作流流程 | 输入→处理→输出 | 左输入，中间BoBee处理，右输出，橙色箭头 |
| 2 | 系统局部 | 信息/模块过滤 | 3-5模块，BoBee参与关键动作 |
| 3 | 前后对比 | 混乱/有序 | 左混乱右稳定，橙色箭头，角色夸张 |
| 4 | 角色状态 | 痛点/卡住/跑起 | 2-4个小状态，每个短标注 |
| 5 | 概念隐喻 | 工厂/仓库/漏斗 | 大怪物件或机器，少量输入输出 |
| 6 | 方法分层 | 框架/层级 | 层叠盒子（非金字塔），BoBee搬砖搭建 |
| 7 | 地图路线 | 路径/承接 | 弯曲路径+节点，BoBee牵线走路 |
| 8 | 小漫画分镜 | 失败→成功 | 2-4格，每格一个动作 |

### 4. Prompt 构建规则
```
Generate one standalone 16:9 horizontal Chinese article illustration.
Pure white background. Hand-drawn doodle illustration style. Warm color palette with soft shading.
Sparse red/orange/blue handwritten Chinese annotations. Lots of empty white space.

Recurring IP: BoBee bee worker [from bobee-ip.md description].
BoBee must perform the core conceptual action, not decorate the scene.

Theme: {文章配图主题}
Structure type: {结构类型}
Core idea: {核心意思}
Composition: {具体画面}
Chinese handwritten labels: {3-5个短标注词}

Constraints: One image one core structure. 40%-60% canvas. No title top-left.
Invent fresh metaphor each time. Clear but not instructional, strange but clean.
```

### 5. 生成命令
```bash
python scripts/generate.py "<prompt>" --model gpt-image2 --res 2k --ratio 16:9 -o output.png
```
