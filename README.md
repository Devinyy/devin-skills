# devin-skills

这个仓库用于存放可复用的 Devin / Codex skill，目前已收录：

- `prd-estimate-doc`
- `smoke-test-executor`

## 当前包含的 skill

### `prd-estimate-doc`

用于把一份 PRD 快速转换成研发侧可执行产物，默认覆盖：

- PRD 结构化摘要
- 前端任务拆解
- 前端技术方案
- 估时文档
- 可选的飞书 Base 排期同步

适用场景：

- 需求评审前，需要快速形成前端评估
- 需要区分真人开发口径和 AI 协同开发口径
- 需要把任务拆到叶子粒度并落到飞书 Base

详情见：

- [prd-estimate-doc/README.md](prd-estimate-doc/README.md)
- [prd-estimate-doc/SKILL.md](prd-estimate-doc/SKILL.md)

### `smoke-test-executor`

用于把冒烟用例清单、Excel 工作簿、PRD 或人工示例转换成可执行验证流程，默认覆盖：

- 冒烟用例抽取与筛选
- UI 点击链执行
- API 辅助数据准备和落库校验
- 失败归因与继续执行策略
- 中文冒烟测试报告

适用场景：

- 测试前，需要从用例表中筛选 P0 或冒烟标签用例
- 需要在真实登录态下验证核心业务流程
- 需要结合网络请求、接口查询和 UI 状态定位问题
- 需要输出包含执行方式、关键校验、记录 ID 和问题分类的报告

详情见：

- [smoke-test-executor/README.md](smoke-test-executor/README.md)
- [smoke-test-executor/SKILL.md](smoke-test-executor/SKILL.md)

## 仓库结构

```text
devin-skills/
├── LICENSE
├── README.md
├── prd-estimate-doc/
│   ├── CHANGELOG.md
│   ├── README.md
│   ├── RELEASE-NOTES.md
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   ├── scripts/
│   └── templates/
└── smoke-test-executor/
    ├── README.md
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/
```

## 安装

如果你只想安装其中一个 skill，可以把对应目录复制到本地：

```text
~/.codex/skills/<skill-name>
~/.agents/skills/<skill-name>
```

## 同步到 cc-switch

如果用 [cc-switch](https://github.com/farion1231/cc-switch) 统一管理 skill，可以用仓库自带的脚本把本仓库的 skill 同步进去：

```bash
./sync-to-cc-switch.sh                  # 同步全部 skill
./sync-to-cc-switch.sh <skill-name> ... # 只同步指定 skill
```

脚本行为：

- 自动发现仓库内含 `SKILL.md` 的目录，`rsync` 到 `~/.cc-switch/skills/<name>`（只补不删，排除 `.DS_Store`/`.git`）
- 新 skill：在 `cc-switch.db` 写入 `local:<name>` 记录（默认对 claude/codex 启用），并在 `~/.claude/skills`、`~/.codex/skills` 建软链；写库前自动备份 DB
- 已存在的 skill：仅刷新文件，不动 DB（`content_hash` 由 cc-switch app 启动时自查重算）

## 快速开始

典型触发方式：

- “用 `prd-estimate-doc` 根据这个 PRD 出估时文档”
- “按 `prd-estimate-doc` 把这份 PRD 同步成 Base 估时表”
- “按 `prd-estimate-doc` 给我一版 AI 协同开发口径估时”
- “用 `smoke-test-executor` 跑这份 Excel 里的 P0 冒烟用例”
- “按 `smoke-test-executor` 设计这份 PRD 的冒烟测试清单”
- “用 `smoke-test-executor` 验证新增流程，UI 操作为主，接口校验落库”

## 发布说明

对外分发可直接参考：

- [prd-estimate-doc/RELEASE-NOTES.md](prd-estimate-doc/RELEASE-NOTES.md)
- [prd-estimate-doc/CHANGELOG.md](prd-estimate-doc/CHANGELOG.md)

`smoke-test-executor` 当前以 README、SKILL 说明和脚本为准，分发前确认不包含真实账号、token、环境配置或业务数据。
