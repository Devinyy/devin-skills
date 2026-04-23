---
name: prd-estimate-doc
version: 1.1.0
description: Use when a PRD needs to be turned into structured delivery documents, frontend task breakdowns, technical design, estimates, or Feishu Base scheduling data
---

# PRD Estimate Doc

`prd-estimate-doc` 用于根据 PRD 快速生成结构化摘要、前端任务拆解、技术方案和估时文档，也适用于将结果同步到飞书 Base 进行研发排期管理。

## 何时使用

以下场景应使用：
- 用户给出 PRD 链接、PRD 原文或附件，要求产出估时文档
- 用户要把需求拆成前端任务、技术方案、估时说明
- 用户要区分真人开发口径和 AI 协同开发口径
- 用户要把估时结果同步到飞书 Base

以下场景不应使用：
- 用户只要阅读 PRD，不需要拆任务或估时
- 用户只要实现代码，不需要先形成文档和估时口径
- 用户要的是后端详细架构设计，而不是需求拆解和排期

## 默认产物

- `docs/product/<topic>-prd-summary.md`
- `docs/product/<topic>-frontend-task-breakdown.md`
- `docs/tech/<topic>-frontend-tech-design.md`
- `docs/project/<topic>-estimate.md`

如果用户正在用飞书 Base 管理估时，再补：
- 明细表父子任务
- 开发 / 联调拆分
- AI 直接实现标记
- 可并行 / 必须串行
- 执行波次

## 工作流

### 1. 先拿到 PRD 原文

优先级：
1. 用户直接提供 PRD 文本或附件
2. 用户提供飞书 Wiki / Doc 链接，先读取正文
3. 如果正文太长，先缓存到本地 markdown，便于后续重复引用

如果是飞书文档：
- 优先使用已有飞书能力读取正文
- 只在读取成功后继续拆解，不要基于标题猜内容

### 2. 输出 4 份核心文档

先阅读 [references/workflow.md](references/workflow.md)。

产出顺序固定：
1. PRD 结构化摘要
2. 前端任务拆解
3. 前端技术方案
4. 估时文档

要求：
- 文件名稳定，便于后续继续引用
- 内容口径一致，任务拆解、技术方案、估时必须互相对齐
- 如果用户没有特别指定，默认只展开前端范围

### 3. 估时时先选口径

先阅读 [references/estimate-rubric.md](references/estimate-rubric.md)。

默认支持两种口径：
- 真人开发口径：前端独立完成开发、联调、自测、回归
- AI 协同开发口径：用户负责边界确认、review、联调，AI 负责大部分实现

如果用户没有明确说明，默认先给真人开发口径；如果用户明确说“我给 PRD，你来实现，我负责 review/联调”，切换到 AI 协同口径。

### 4. 拆解规则

- 先按模块拆，再按页面或能力拆，再按可执行子任务拆
- 父任务只做分组，不直接承担估时
- 叶子任务才写工时
- 如果用户需要进入飞书 Base 管理，叶子任务建议控制在 `<= 4h`
- 联调、自测、全链路回归单独成项，不要混在开发工时里

### 5. 技术方案规则

技术方案至少覆盖：
- 模块归属和子应用边界
- 页面或组件复用策略
- 接口分层和请求口径
- 权限、店铺上下文、路由、状态管理
- 风险点和待确认项

方案必须服务于本次需求拆解和估时，不写泛泛架构说明。

### 6. 飞书 Base 同步规则

如果用户要求把估时写回飞书 Base：
- 先确认表结构、字段、父子任务关系
- 父任务工时清空，只做容器
- 汇总表只汇总叶子任务
- 常见字段包括：`工时(h)`、`阶段`、`备注`、`Parent items`
- 如需 AI 协同排期，可继续增加：`AI直接实现`、`执行方式`、`执行波次`

涉及 Base 字段或记录写入时，优先使用相关 Base 能力，不要凭空猜字段 ID。

### 7. Base 批量写入优先使用脚本

当同一张 Base 需要批量重写几十条记录时，先阅读 [references/base-sync.md](references/base-sync.md)。

本 skill 内置两类脚本：
- `scripts/rewrite-base-leaf-tasks.js`
  用于把父任务改成容器、按叶子任务工时重写明细表
- `scripts/apply-ai-schedule-fields.js`
  用于批量补 `AI直接实现`、`执行方式`、`执行波次`

脚本模板：
- `templates/rewrite-base-config.example.json`
- `templates/ai-schedule-config.example.json`

适用条件：
- 已经确认表结构稳定
- 需要批量重写几十条记录
- 任务口径已经确定，不再需要临场做产品判断

## 输出标准

一份合格的估时结果，至少要满足：
- 有结构化摘要，不依赖重新读 PRD
- 有任务拆解，可直接映射开发工作项
- 有技术方案，能解释为什么这么拆
- 有估时说明，明确口径、风险和假设
- 如果写入飞书 Base，父子任务关系清晰，汇总不重复计时

## 常见坑

- 只做总工时，不拆开发/联调，后续排期会失真
- 直接按页面估时，不拆关键交互和数据流转，容易低估
- 把父任务和子任务同时计时，导致汇总重复累计
- AI 协同口径下，仍沿用纯人工开发工时，导致结论偏大
- 没把待确认项写出来，后续估时很难解释

## 参考

- [README.md](README.md)
- [references/workflow.md](references/workflow.md)
- [references/estimate-rubric.md](references/estimate-rubric.md)
- [references/base-sync.md](references/base-sync.md)
- [references/publish-checklist.md](references/publish-checklist.md)
