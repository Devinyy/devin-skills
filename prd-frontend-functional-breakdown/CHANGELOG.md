# Changelog

## 2.0.0 - 2026-07-20

### Changed

- 将技能收敛为仅处理 PRD → 前端功能拆解
- 将技能重命名为 `prd-frontend-functional-breakdown`
- 固定拆解层级为：端 → 页面 → 模块 → 字段 → 功能 → 逻辑
- 将技术方案、估时与飞书 Base 回填能力移入 `deferred-delivery-workflow/` 暂存，待后续拆分

## 1.1.0 - 2026-04-23

### Added

- 新增 `README.md`，补充安装、使用、分发建议和脚本前置条件
- 新增 `RELEASE-NOTES.md`，提供可直接转发给同事的对外发布说明
- 新增 `references/publish-checklist.md`，用于打包和交付前检查
- 新增 `templates/rewrite-base-config.example.json`
- 新增 `templates/ai-schedule-config.example.json`
- 新增 `agents/openai.yaml`，补充 skill 元数据

### Changed

- 将 `SKILL.md` 收敛为更适合正式分发的版本
- 将 description 改为更适合技能检索和自动触发的写法
- 将 `references/base-sync.md` 改为模板化、可分发的脚本使用说明
- 将 Base 批量脚本改为基于配置文件驱动，而不是写死项目参数

### Fixed

- 移除分发包中的 `.DS_Store`
- 补齐脚本 usage 和配置说明，保证他人拿到后可直接理解执行方式

## 1.0.0 - 2026-04-23

### Added

- 首版 `prd-estimate-doc` skill
- 支持从 PRD 生成结构化摘要、前端任务拆解、技术方案和估时文档
- 支持真人开发口径和 AI 协同开发口径
- 新增 `references/workflow.md`
- 新增 `references/estimate-rubric.md`
- 新增 `references/base-sync.md`
- 新增 `scripts/rewrite-base-leaf-tasks.js`
- 新增 `scripts/apply-ai-schedule-fields.js`
