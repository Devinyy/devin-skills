# qiniu-icon-upload

> [English](./README.md) | 简体中文

一个命令行工具（同时也是 Claude Code skill），用于将 Figma 切图图标转换为托管在七牛云
（Qiniu）CDN 上的 URL，并将其接入代码 —— 导出透明 PNG → 上传（支持复用 + 分类）→
替换代码中的 URL。

它有两种使用方式：

- **作为普通命令行工具** —— 在任意 shell 或 CI 流水线中直接运行 `scripts/*.py`。
  上传器为纯 Python 标准库实现（无需七牛云 SDK），可直接嵌入任何环境。
- **作为 Claude Code skill** —— 将该文件夹放入你的 skills 目录，让 agent 执行完整的
  Figma→上传→替换 工作流。详见 `SKILL.md`。

## 安装配置

```bash
cp config.example.json config.local.json
# 编辑 config.local.json：填写 access_key、secret_key、bucket、domain
```

`config.local.json` 保存你的密钥，已被 **gitignore** 忽略 —— 切勿提交到仓库。

环境要求：Python 3（上传器为纯标准库实现，无需七牛云 SDK）。`prepare_png.py`
需要 Pillow；SVG 栅格化可选用 `cairosvg` 或 `rsvg-convert`。

## 快速使用

```bash
# 仅分类（不联网）
python3 scripts/qiniu_upload.py classify back.png
python3 scripts/qiniu_upload.py classify banner_top.png --page home

# 上传（如果同名且内容相同已存在于七牛云，则复用）
python3 scripts/qiniu_upload.py upload tmp-icons/back.png            # -> common/back.png
python3 scripts/qiniu_upload.py upload tmp-icons/banner_top.png --page home

# 准备透明 PNG（校验 alpha 通道 / 裁剪 / 栅格化 SVG）
python3 scripts/prepare_png.py in.svg out.png --scale 3
```

每次 `upload`/`classify` 都会在 stdout 输出一行 JSON，包含最终的 `url`，便于接入脚本、
CI 步骤或其他工具。

## 工作原理

| 规则 | 行为 |
|------|------|
| 复用 | 先 `stat` 该 key；同名 + 内容哈希相同 → 复用 URL（不上传）。内容变化 → 覆盖。 |
| 分类 | 名称匹配通用前缀/关键词时归入 `common/`，否则归入 `<page>/`（需提供 `--page`）。清单见 config。 |
| 替换 | 输出 CDN URL；由你（或 agent）替换代码中本地的 `/static/icon/...` 路径。 |

完整的 Figma→上传→替换 工作流（Claude Code 模式）见 `SKILL.md`，命名规则见
`references/classification.md`。
