# devin-skills

这个仓库用于存放可复用的 Devin / Codex skill，目前已收录：

- `figma-fidelity-check`
- `figma-tech-design-to-code`
- `frontend-architecture-map`
- `humanizer-zh`
- `openapi-md-doc`
- `prd-figma-info`
- `prd-frontend-functional-breakdown`
- `prd-frontend-tech-design`
- `qiniu-icon-upload`
- `smoke-test-executor`
- `video-knowledge-skill`

## 当前包含的 skill

### `figma-fidelity-check`

用于通过截图对比验证 UI 实现对 Figma 设计稿的还原度，覆盖 PC/H5 和微信小程序原生截图场景。

详情见：

- [figma-fidelity-check/SKILL.md](figma-fidelity-check/SKILL.md)

### `figma-tech-design-to-code`

用于根据带 `node-id` 的 Figma 链接、前端技术方案和目标仓库实现可验证的前端代码，并完成还原度校验。

详情见：

- [figma-tech-design-to-code/SKILL.md](figma-tech-design-to-code/SKILL.md)

### `frontend-architecture-map`

用于绘制分层能力地图风格的前端、业务、平台或系统架构图，适合表达宿主、业务、组件、基础能力、中台能力、运维能力等关系。

详情见：

- [frontend-architecture-map/README.md](frontend-architecture-map/README.md)
- [frontend-architecture-map/SKILL.md](frontend-architecture-map/SKILL.md)

### `humanizer-zh`

用于编辑或审阅中文文本，去除常见 AI 写作痕迹，让内容更自然、更像真人书写。

详情见：

- [humanizer-zh/README.md](humanizer-zh/README.md)
- [humanizer-zh/SKILL.md](humanizer-zh/SKILL.md)

### `openapi-md-doc`

用于把 OpenAPI / Swagger 的 `api-docs` URL 或 JSON 文件转换成字段级 Markdown 接口文档，方便前端集成。

详情见：

- [openapi-md-doc/README.md](openapi-md-doc/README.md)
- [openapi-md-doc/SKILL.md](openapi-md-doc/SKILL.md)

### `prd-figma-info`

用于从 Figma 设计稿采集可供前端实现、评审和技术方案引用的页面、组件、样式、交互、资源和覆盖范围信息。

详情见：

- [prd-figma-info/SKILL.md](prd-figma-info/SKILL.md)

### `prd-frontend-functional-breakdown`

用于把 PRD 或飞书文档转换成前端功能拆解文档，在技术方案、估时或实现前先确认需求边界。

详情见：

- [prd-frontend-functional-breakdown/README.md](prd-frontend-functional-breakdown/README.md)
- [prd-frontend-functional-breakdown/SKILL.md](prd-frontend-functional-breakdown/SKILL.md)

### `prd-frontend-tech-design`

用于根据 PRD、前端功能拆解、Figma 信息和现有代码仓库，编写可评审、可执行的前端技术方案。

详情见：

- [prd-frontend-tech-design/SKILL.md](prd-frontend-tech-design/SKILL.md)

### `qiniu-icon-upload`

用于把本地图标切图上传到七牛云 CDN，并将代码中的本地 `/static/icon` 路径替换为 CDN URL。

详情见：

- [qiniu-icon-upload/README.md](qiniu-icon-upload/README.md)
- [qiniu-icon-upload/SKILL.md](qiniu-icon-upload/SKILL.md)

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

### `video-knowledge-skill`

用于从 Bilibili、抖音、小红书、微信公众号/视频号、公开网页文章、本地视频或音频中提取字幕、总结、转笔记，并导出到 Markdown / 飞书 / Obsidian。

详情见：

- [video-knowledge-skill/README.md](video-knowledge-skill/README.md)
- [video-knowledge-skill/SKILL.md](video-knowledge-skill/SKILL.md)
- [video-knowledge-skill/SKILL.zh.md](video-knowledge-skill/SKILL.zh.md)

## 仓库结构

```text
devin-skills/
├── figma-fidelity-check/
│   ├── SKILL.md
│   └── report-template.md
├── figma-tech-design-to-code/
│   ├── SKILL.md
│   └── agents/
├── frontend-architecture-map/
│   ├── README.md
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── templates/
├── humanizer-zh/
│   ├── README.md
│   └── SKILL.md
├── LICENSE
├── openapi-md-doc/
│   ├── README.md
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   ├── scripts/
│   └── templates/
├── README.md
├── prd-figma-info/
│   ├── SKILL.md
│   ├── agents/
│   └── references/
├── prd-frontend-functional-breakdown/
│   ├── CHANGELOG.md
│   ├── README.md
│   ├── RELEASE-NOTES.md
│   ├── SKILL.md
│   ├── agents/
│   ├── deferred-delivery-workflow/
│   └── references/
├── prd-frontend-tech-design/
│   ├── SKILL.md
│   ├── agents/
│   └── references/
├── qiniu-icon-upload/
│   ├── README.md
│   ├── README.zh-CN.md
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── smoke-test-executor/
│   ├── README.md
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
└── video-knowledge-skill/
    ├── README.md
    ├── SKILL.md
    ├── SKILL.zh.md
    ├── extractors/
    ├── references/
    ├── scripts/
    ├── tests/
    └── workflows/
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

- “用 `figma-fidelity-check` 对比这个页面和 Figma 的还原度”
- “用 `figma-tech-design-to-code` 按技术方案还原这个 Figma 页面”
- “用 `frontend-architecture-map` 画一张前端业务架构图”
- “用 `humanizer-zh` 把这段文案改得不像 AI 写的”
- “用 `openapi-md-doc` 把这个 `/v3/api-docs` 转成 Markdown 接口文档”
- “用 `prd-figma-info` 梳理这个 Figma 设计稿的页面、组件和交互信息”
- “用 `prd-frontend-functional-breakdown` 先把这份 PRD 拆成前端功能清单”
- “用 `prd-frontend-tech-design` 根据 PRD、功能拆解和 Figma 信息写前端技术方案”
- “用 `qiniu-icon-upload` 上传这些切图到七牛云并替换代码链接”
- “用 `smoke-test-executor` 跑这份 Excel 里的 P0 冒烟用例”
- “按 `smoke-test-executor` 设计这份 PRD 的冒烟测试清单”
- “用 `smoke-test-executor` 验证新增流程，UI 操作为主，接口校验落库”
- “用 `video-knowledge-skill` 总结这个视频并转成 Obsidian 笔记”

## 发布说明

对外分发可直接参考：

- [prd-frontend-functional-breakdown/RELEASE-NOTES.md](prd-frontend-functional-breakdown/RELEASE-NOTES.md)
- [prd-frontend-functional-breakdown/CHANGELOG.md](prd-frontend-functional-breakdown/CHANGELOG.md)

其他 skill 当前以 README、SKILL 说明和脚本为准，分发前确认不包含真实账号、token、环境配置或业务数据。
