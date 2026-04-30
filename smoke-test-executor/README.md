# Smoke Test Executor

`smoke-test-executor` 用于把冒烟用例清单、Excel 工作簿、PRD 或人工示例转换成可执行验证流程，并输出 UI/API 结合的中文测试报告。

## 适用场景

- 有一份冒烟用例表，需要按优先级、模块、标签筛选并执行
- 需要在真实登录态和测试环境中走 UI 点击链验证核心流程
- 需要用接口辅助准备测试数据、定位请求响应、确认落库结果
- 需要对失败用例做问题归因，并形成简洁的中文执行报告

## 包内容

- `SKILL.md`
  正式 skill 入口，定义触发时机、用例抽取、执行策略、失败处理和报告格式
- `agents/openai.yaml`
  Skill 元数据，供 UI 或分发工具识别
- `references/example-case-shape.md`
  冒烟用例表结构示例，仅作为字段形态参考
- `scripts/extract_smoke_cases.py`
  从 `.xlsx` 工作簿抽取并标准化冒烟用例，支持关键词、优先级和标签筛选

## 安装

将整个目录复制到目标环境的：

```text
~/.codex/skills/smoke-test-executor
```

如果使用 Devin 或其他兼容 agents skill 目录的环境，也可以复制到：

```text
~/.agents/skills/smoke-test-executor
```

## 使用

典型触发方式：

- “用 `smoke-test-executor` 跑这份 Excel 里的 P0 冒烟用例”
- “按 `smoke-test-executor` 设计这份 PRD 的冒烟测试清单”
- “用 `smoke-test-executor` 验证价格规则新增流程，UI 操作为主，接口校验落库”

## 脚本前置条件

- 本机 Python 版本支持 `python3`
- 已安装 `openpyxl`
- 输入文件为 `.xlsx` 工作簿，首行包含可识别的用例表头

安装依赖示例：

```bash
python3 -m pip install openpyxl
```

抽取用例示例：

```bash
python3 ~/.codex/skills/smoke-test-executor/scripts/extract_smoke_cases.py cases.xlsx --priority P0 --tag 冒烟测试
```

输出为标准化 JSON，字段包括 `caseId`、`title`、`modulePath`、`precondition`、`steps`、`expected`、`priority`、`type` 和 `tags`。

## 执行建议

- UI 路径优先，接口只用于数据准备、请求定位和持久化校验
- 写入测试数据前确认目标环境、登录态和清理规则
- 测试数据命名使用稳定前缀和时间戳，便于追踪与清理
- 失败时保留用例 ID、步骤、URL、请求响应、控制台错误和问题分类

## 分发建议

- 不要把真实账号、token、测试环境敏感配置或业务数据一起打包
- 示例文件只保留字段形态，不绑定具体业务域
- 首次给别人使用前，用一个小型 `.xlsx` 文件验证脚本抽取和报告格式
