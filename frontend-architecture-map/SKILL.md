---
name: frontend-architecture-map
version: 1.0.0
description: Use when a frontend, business, platform, capability, or system architecture diagram should be drawn in a layered capability-map style similar to the user's Feishu reference architecture map
---

# Frontend Architecture Map

用于按“我店生活大前端业务架构”风格绘制架构图。这个 skill 的重点不是普通流程图，而是分层能力地图：用横向层级、能力域分组、状态颜色和模块卡片表达复杂业务/前端/平台架构。

## 何时使用

以下场景应使用：
- 用户要求画架构图、业务架构图、前端架构图、能力地图、平台能力图
- 用户说“按之前那个架构图风格”“按模板画”“画成分层能力图”
- 需要表达宿主、业务、组件、基础能力、中台能力、运维能力之间的关系
- 需要在飞书画板中生成可视化架构图

以下场景不应使用：
- 简单流程、决策树、时序链路优先用 Mermaid 流程图
- 只需要代码模块说明，不需要画图
- 需要精确 UML 类图或 ER 图

## 核心风格

先阅读 [references/style-guide.md](references/style-guide.md)。

输出图应符合以下特征：
- 横向大画布
- 顶部有图例
- 主标题用黑底白字横条
- 左侧是层级标签
- 中间按能力域分组
- 小模块用矩形卡片
- 关键域用浅蓝底大容器包裹
- 底部可放大前端中台能力、开发域、运维域、运营域

## 默认层级

优先按以下层级组织：
1. 宿主层
2. 业务层
3. 组件层
4. 基础层
5. 大前端中台能力
6. 开发域
7. 运维域
8. 运营域

如果用户给的是非前端架构，可以保留“分层能力地图”的结构，但替换层级名称。

## 状态图例

固定使用以下语义：
- 已实现：绿色
- 建设中：青色
- 未建设：灰色
- 即将/已废弃：黑色
- 其他部门支持：橙色

## 绘制流程

1. 先整理输入信息，识别：
   - 宿主或入口
   - 业务域
   - 组件能力
   - 基础能力
   - 平台/中台能力
   - 运维与运营能力
   - 每个能力的建设状态
2. 如果信息不足，基于常见前端架构做合理分组，不要停下来问太多问题。
3. 先输出一份结构化分层清单。
4. 再生成图。
5. 如果目标是飞书，优先使用 `lark-whiteboard` 画板能力。

## 输出要求

架构图必须做到：
- 一眼能看出层级
- 一眼能看出哪些能力已实现、建设中、未建设
- 业务域和基础能力不要混在一起
- 不要画成线条复杂的流程图
- 颜色只用于状态和层级，不要随机上色

## 推荐实现方式

优先级：
1. 飞书画板 DSL / raw 结构
2. SVG 转飞书画板
3. Mermaid 作为降级方案

如果使用 Mermaid，只适合低保真草图；正式图应优先使用画板或 SVG，以便做出接近参考图的大画布分区效果。

## 参考

- [references/style-guide.md](references/style-guide.md)
- [templates/layered-capability-map.md](templates/layered-capability-map.md)
