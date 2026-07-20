# PRD Frontend Functional Breakdown 对外发布说明

这里提供一个可直接复用的 `prd-frontend-functional-breakdown` skill，用于把一份 PRD 转换为可确认、可追溯的前端功能拆解，减少重复读 PRD 和反复确认功能范围的成本。

## 这个 skill 解决什么问题

它适合在拿到 PRD 后，快速产出：

- 前端功能拆解：端、页面、模块、字段、功能、逻辑
- 跨页面业务逻辑与待确认项

## 适用场景

- 需求评审前，需要快速确认前端范围
- 需要将 PRD 规范地拆到端、页面、模块、字段、功能和逻辑
- 需要明确 PRD 的缺失、冲突和待确认项

## 包内包含什么

- `SKILL.md`
  定义 skill 的适用时机、工作流和产物要求
- `README.md`
  安装说明和使用方式
- `references/`
  前端功能拆解工作流和文档模板
- `deferred-delivery-workflow/`
  待后续拆分的技术方案、估时与 Base 回填能力

## 安装方式

把目录安装到：

```text
~/.agents/skills/prd-frontend-functional-breakdown
```

## 推荐触发方式

- “用 `prd-frontend-functional-breakdown` 根据这个 PRD 做前端功能拆解”
- “按 `prd-frontend-functional-breakdown` 将这份 PRD 拆成端、页面、模块、字段、功能和逻辑”

## 使用前提

- 提供 PRD 正文、附件，或可读取正文的飞书文档链接

## 注意事项

- 不应把真实 PRD、账号信息或项目私有数据打包到技能中
- UI、接口、路由和技术实现不在本技能范围内

## 当前版本

- 版本：`2.0.0`
- 能力范围：PRD 前端功能拆解
