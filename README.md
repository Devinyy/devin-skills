# devin-skills

这个仓库用于存放可复用的 Devin / Codex skill，目前已收录：

- `prd-estimate-doc`

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

## 仓库结构

```text
devin-skills/
├── LICENSE
├── README.md
└── prd-estimate-doc/
    ├── CHANGELOG.md
    ├── README.md
    ├── RELEASE-NOTES.md
    ├── SKILL.md
    ├── agents/
    ├── references/
    ├── scripts/
    └── templates/
```

## 安装

如果你只想安装其中一个 skill，可以把对应目录复制到本地：

```text
~/.agents/skills/prd-estimate-doc
```

## 快速开始

典型触发方式：

- “用 `prd-estimate-doc` 根据这个 PRD 出估时文档”
- “按 `prd-estimate-doc` 把这份 PRD 同步成 Base 估时表”
- “按 `prd-estimate-doc` 给我一版 AI 协同开发口径估时”

## 发布说明

对外分发可直接参考：

- [prd-estimate-doc/RELEASE-NOTES.md](prd-estimate-doc/RELEASE-NOTES.md)
- [prd-estimate-doc/CHANGELOG.md](prd-estimate-doc/CHANGELOG.md)
