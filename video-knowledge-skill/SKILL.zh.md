---
name: video-knowledge-skill-zh
description: Use when a user provides Bilibili、抖音、小红书、微信公众号文章/视频号、公开视频/音频、公开网页文章链接或本地音视频文件，并要求阅读、总结、提取字幕/转写、转成笔记、沉淀知识库、导出 Markdown/飞书/Obsidian，或批量处理素材。
---

# 视频知识沉淀技能

## 目的

本技能用于从主流视频链接、公开文章、本地视频或本地音频中提取知识，并转换成可保存到知识库的结构化笔记。

主要目标：

> 视频链接 / 文章链接 / 本地音视频 → 元数据 → 音频 / 正文 → 转写 / 抽取 → 结构化摘要 → Markdown / 飞书文档 / Obsidian 笔记

## 支持输入

- Bilibili 视频链接
- 抖音视频链接
- 小红书笔记或视频链接
- 微信公众号文章链接，包括含内嵌视频的文章
- 微信视频号链接，或用户手动导出的视频文件
- 通用公开网页文章，例如 SegmentFault、cnblogs.com、知乎专栏、官方博客
- 本地视频或音频文件

## 可靠性策略

不同平台有不同的反爬、登录和权限限制。本技能不能承诺所有链接都能全自动处理。

| 平台 | 优先策略 | 可靠性 |
| --- | --- | --- |
| Bilibili | 优先 yt-dlp，可选 cookies | 高 |
| 抖音 | 优先 yt-dlp，Playwright 浏览器兜底，可选 cookies | 中 |
| 小红书 | 优先 yt-dlp，补充笔记正文抽取，可选 cookies | 中 |
| 微信公众号文章 | 优先文章解析，内嵌媒体尽力处理 | 中 |
| 微信视频号 | 尽力提取媒体，优先建议本地文件兜底；拒绝仅预览页 | 低 |
| 通用文章 | HTML 文章解析，尽力抽取主体正文 | 中 |
| 本地文件 | ffmpeg + faster-whisper / mlx-whisper | 高 |

## 触发场景

当用户提出以下需求时使用本技能：

- 阅读、总结、提炼一个公开网页文章链接
- 总结视频、音频或公开视频链接
- 提取视频字幕、音频转写或完整 transcript
- 把视频、音频、文章转换成可收藏笔记
- 从 Bilibili、抖音、小红书、微信公众号、视频号链接中提取要点
- 总结 SegmentFault、cnblogs.com、知乎专栏、官方博客等公开文章
- 将文章、视频或音频沉淀为 Markdown / Obsidian / 飞书知识库笔记
- 批量处理多个视频、音频或文章链接

## 工作流

### 单条视频 / 文章抽取

使用 `workflows/single-video-extract.md`。

### 批量抽取

使用 `workflows/batch-video-extract.md`。

### 仅转写 / 字幕抽取

使用 `workflows/transcript-extract.md`。

### 飞书 / Lark 导出

使用 `workflows/export-to-feishu.md`。

## 执行契约

每个任务应产出如下文件：

```txt
outputs/{task_id}/
├── metadata.json
├── transcript.json
├── transcript.md
├── summary.md
├── {主标题}.md
└── assets/
```

纯文章或仅正文类链接可以只产出 `article.md` 和 `summary.md`，不要求产出 transcript 文件。

标题版 Markdown 文件名来自生成摘要中的第一个 `# ` 一级标题，例如 `字节跳动技术副总裁洪定坤：AI Coding 的实践与探索.md`。

如果检测到本地 Obsidian vault，默认将同一份标题版笔记复制到 vault 根目录下自动选择的二级分类中，例如 `研发/DevOps/` 或 `AI工程/Agent/`。分类优先使用配置的 LLM，不可用时回退到本地规则。Obsidian 笔记会追加 `## Obsidian 关联`，并链接 `主题/` 下的扁平主题笔记。

可用环境变量：

- `OBSIDIAN_VAULT_PATH`：指定 Obsidian vault
- `OBSIDIAN_OUTPUT_DIR`：指定 vault 内输出子目录
- `OBSIDIAN_CATEGORY`：强制分类路径
- `OBSIDIAN_CLASSIFIER=rules`：跳过模型分类，使用规则分类
- `--no-obsidian`：跳过 Obsidian 导出

每个生成的 `summary.md` 和标题版 Markdown 文件都必须包含 `## 原链接`，记录原始 URL 或本地源路径。

抖音 cookies 过期时，只在 yt-dlp 明确提示需要新 cookies 后自动刷新。刷新逻辑使用本地浏览器中的已登录会话，不自动绕过验证码、短信、扫码登录或风控验证。

## 最终回复契约

成功抽取并总结后，回复必须包含：

1. `outputs/{task_id}/summary.md` 的绝对路径。
2. 标题版 Markdown 的绝对路径。
3. Obsidian 导出成功时，给出 Obsidian 笔记绝对路径。
4. `summary.md` 的完整 Markdown 内容。

不要只说“摘要已生成”。如果用户要求“输出”“结果”“笔记”等，应从磁盘读取 `summary.md` 并粘贴完整内容。

批量处理时，回复队列状态和每个成功任务的 `summary.md` 绝对路径。如果用户要求内容，则包含对应任务的完整 `summary.md` 内容。

## 核心命令

检查环境：

```bash
bash scripts/check-env.sh
```

识别平台：

```bash
python scripts/detect-platform.py "<url-or-file>"
```

抽取单条素材：

```bash
python scripts/extract-video.py "<url-or-file>" --output outputs
python scripts/extract-video.py "<url-or-file>" --output outputs --transcribe --summarize --transcribe-backend mlx --model-size small --summary-style dual
```

批量抽取：

```bash
python scripts/batch-extract.py inputs.txt --output outputs --transcribe --summarize --transcribe-backend mlx --model-size small
python scripts/batch-extract.py inputs.txt --output outputs --resume
```

查看和清理输出：

```bash
python scripts/list-outputs.py outputs
python scripts/clean-empty-outputs.py outputs
```

## 边界

- 不绕过付费墙或私有访问限制。
- 不抽取未授权的私密账号内容。
- 平台限制明显时，优先使用官方 API 或用户提供的导出文件。
- 微信视频号只做尽力处理。如果页面只有预览文本、元数据，没有可播放媒体、转写或实质正文，应明确失败，不生成占位笔记。
