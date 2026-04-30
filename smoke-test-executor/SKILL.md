---
name: smoke-test-executor
description: Use when executing or designing smoke tests from a checklist, Excel workbook, PRD, test case table, or manual example; supports UI click-chain verification, API-assisted setup/verification, real-login environment checks, failure triage, and concise Chinese test reports.
---

# Smoke Test Executor

## Purpose

Use this skill to turn a smoke test checklist into an executable validation flow. The default stance is: core business actions are verified through the UI path; APIs may assist with fixture discovery, setup, response inspection, and final data verification.

## Inputs To Gather

- Test source: Excel/CSV/Markdown table/PRD/manual cases.
- Target scope: module, page, case IDs, priority, or tag.
- Runtime rule: project root command, login source, test environment, and whether real data writes are allowed.
- Cleanup rule: keep created data, disable it, delete it, or only mark it in the report.

If the user gives an example workbook, treat it as case-shape reference. Do not hard-code its business domain unless the user asks for that domain.

## Case Extraction

For Excel or CSV, normalize each row into:

- `caseId`
- `title`
- `modulePath`
- `precondition`
- `steps`
- `expected`
- `priority`
- `type`
- `tags`

Prefer P0 and rows tagged as smoke tests unless the user specifies another scope. Use `scripts/extract_smoke_cases.py` when useful:

```bash
python3 /Users/zhangxiang/.codex/skills/smoke-test-executor/scripts/extract_smoke_cases.py path/to/cases.xlsx --keyword 价格 --priority P0
```

## Execution Policy

1. Start the app exactly as the project/user requires. If the user says to start from the repository root to preserve login/token, do that.
2. Confirm the browser has a valid authenticated state before running destructive or write cases.
3. Drive the primary user journey through UI clicks, typing, selects, modals, and form submission.
4. Use API calls only for:
   - finding stable fixture data;
   - confirming network request/response mapping;
   - checking persisted values after UI completion;
   - preparing state when the case precondition cannot be reached through UI in reasonable time.
5. Do not replace a UI smoke case with direct backend writes unless the user explicitly approves it.
6. If selectors are unstable, add or recommend stable `data-testid` attributes before relying on brittle text or DOM structure.

## Data Strategy

- Use deterministic names with a clear prefix, timestamp, or incrementing suffix, for example `zx冒烟-规则-商品-固定-20260430-1530`.
- Use real fixture IDs discovered from the current environment, not guessed IDs.
- Before batch writes, state the environment and the number/type of records to create if user confirmation is needed.
- Track created record IDs in the report so follow-up cleanup is possible.

## Validation Matrix

For each case, verify at least:

- UI state: visible page, form values, table row, detail page, status label, inline validation, disabled/loading/empty/error states when relevant.
- Network: expected endpoint called, request payload mapping, response code/message/data shape.
- Persistence: list/detail/API query reflects the user-visible result.
- Negative path: required validation appears inline when specified, duplicate submit is blocked, failed request is reported predictably.

When testing forms, required-field errors should be checked in the form surface if the product requirement says not to use toast.

## Failure Handling

When a step fails:

1. Capture the failing case ID, step, URL, selector/action, network response, and console errors.
2. Classify the issue as test data, environment/login, selector/test script, frontend logic, adapter/API mapping, or backend behavior.
3. If it is a code or selector issue in the current workspace and the user asked to execute/fix, patch it and rerun the failed case.
4. If it is a backend/data/environment blocker, stop only the affected case and continue independent cases when safe.

## Report Format

Respond in Chinese with a compact table:

| 用例 | 执行方式 | 结果 | 关键校验 | 产物/记录ID | 问题 |
|---|---|---|---|---|---|

Then list:

- 启动方式与环境
- 已创建/修改的数据
- 失败或跳过原因
- 已修复内容
- 仍需人工确认的问题

## References

- Read `references/example-case-shape.md` only when you need a concrete example of the supported workbook shape.
