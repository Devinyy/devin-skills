# PRD Estimate Doc

`prd-estimate-doc` 用于根据 PRD 生成结构化摘要、前端任务拆解、技术方案和估时文档，并可继续同步到飞书 Base 做研发排期管理。

## 适用场景

- 产品给出一份新 PRD，需要快速完成前端评估
- 需要区分真人开发口径和 AI 协同开发口径
- 需要把任务拆到叶子级并同步到飞书 Base
- 需要输出稳定的 markdown 文档，方便后续继续引用

## 包内容

- `SKILL.md`
  正式 skill 入口，定义使用时机、工作流和产物要求
- `RELEASE-NOTES.md`
  对外发布说明，适合直接转发给同事
- `agents/openai.yaml`
  Skill 元数据，供 UI 或分发工具识别
- `references/workflow.md`
  文档产出顺序和建议结构
- `references/estimate-rubric.md`
  估时口径与分项规则
- `references/base-sync.md`
  飞书 Base 原子写入与批量写入的使用边界
- `references/publish-checklist.md`
  打包、交付、验收前检查项
- `templates/*.example.json`
  Base 批量脚本的配置模板
- `scripts/*.js`
  Base 批量重写和 AI 排期字段回写脚本

## 安装

将整个目录复制到目标环境的：

```text
~/.agents/skills/prd-estimate-doc
```

如果已有同名 skill，先备份再覆盖。

## 使用

典型触发方式：

- “用 `prd-estimate-doc` 根据这个 PRD 出估时文档”
- “按 `prd-estimate-doc` 把这份 PRD 同步成 Base 估时表”
- “按 `prd-estimate-doc` 给我一版 AI 协同开发口径估时”

## 脚本前置条件

- 本机已安装 `lark-cli`
- 当前用户已经完成飞书授权
- 已能读取目标 Base 的表结构和记录

## 分发建议

- 不要把真实 `baseToken`、表 ID、用户数据 JSON 一起打包
- 只分发模板、脚本和说明文档
- 首次给别人使用前，按 `references/publish-checklist.md` 自测一遍
