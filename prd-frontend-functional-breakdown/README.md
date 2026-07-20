# PRD Frontend Functional Breakdown

`prd-frontend-functional-breakdown` 用于根据 PRD 生成前端功能拆解，不覆盖技术方案、估时或飞书 Base 排期。

## 适用场景

- 产品给出一份新 PRD，需要先确认前端功能范围
- 需要按端、页面、模块、字段、功能、逻辑拆解需求
- 需要输出稳定的 Markdown 文档，供后续技术方案或估时继续引用

## 包内容

- `SKILL.md`
  正式 skill 入口，定义使用时机、工作流和产物要求
- `RELEASE-NOTES.md`
  对外发布说明，适合直接转发给同事
- `agents/openai.yaml`
  Skill 元数据，供 UI 或分发工具识别
- `references/workflow.md`
  前端功能拆解的文档模板和边界规则
- `deferred-delivery-workflow/`
  原技术方案、估时和 Base 回填能力的暂存内容，待后续拆分为独立技能

## 安装

将整个目录复制到目标环境的：

```text
~/.agents/skills/prd-frontend-functional-breakdown
```

如果已有同名 skill，先备份再覆盖。

## 使用

典型触发方式：

- “用 `prd-frontend-functional-breakdown` 根据这个 PRD 做前端功能拆解”
- “按 `prd-frontend-functional-breakdown` 将这份 PRD 拆成端、页面、模块、字段、功能和逻辑”

## 分发建议

- 不要把真实 PRD、账号信息或项目私有数据一起打包
- 前端功能拆解必须只引用已确认的 PRD 内容
