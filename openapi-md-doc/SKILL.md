---
name: openapi-md-doc
version: 1.0.0
description: Use when an OpenAPI or Swagger api-docs URL or JSON file needs to be converted into a field-level Markdown API document for frontend integration
---

# OpenAPI Markdown Doc

用于把 OpenAPI / Swagger 的 `api-docs` 地址或 JSON 文件整理成字段级 Markdown 接口文档。输出必须包含接口目录、分组、入参参数结构和响应结构体，方便后续前端调用。

## 何时使用

以下场景应使用：
- 用户给出类似 `/v3/api-docs`、`/swagger.json`、`openapi.json` 的接口地址
- 用户要求整理接口文档、接口清单、入参和响应结构
- 用户需要 Markdown 格式 API 文档供前端开发查看
- 用户明确说后续会用这些接口进行调用或联调

以下场景不应使用：
- 用户只问某一个接口怎么调用，可以直接分析单接口
- 用户要生成 TypeScript SDK，而不是 Markdown 文档
- 用户给的是 Apifox MCP 工具结果，但没有 OpenAPI JSON 内容

## 输出标准

字段级 API 文档必须包含：
- 来源地址或来源文件
- OpenAPI / Swagger 版本
- 标题、版本、path 数、tag 数、schema 数
- 分组概览
- 每个接口的：
  - Method
  - Path
  - Summary
  - OperationId
  - Parameters
  - Request Body
  - Responses
- 对 request/response 中的 `$ref` 结构进行展开
- 字段表至少包含：字段、类型、必填、默认值、说明

## 推荐流程

1. 如果用户给 URL，先下载 OpenAPI JSON 到临时文件。
2. 如果网络失败，按当前环境规则请求网络权限后重试。
3. 运行内置脚本生成 Markdown。
4. 回读文档开头和至少一个包含 request/response 的接口，确认字段已展开。
5. 告知用户输出文件路径和统计结果。

## 脚本

优先使用：

```bash
node scripts/generate-openapi-md.js --input <url-or-json-file> --output <output.md>
```

示例：

```bash
node scripts/generate-openapi-md.js \
  --input http://101.132.156.77:8520/admin-app/v3/api-docs \
  --output docs/api/admin-app-v3-api-docs.md
```

可选参数：
- `--title <title>`：覆盖文档标题
- `--source <source>`：覆盖文档来源展示文本
- `--max-depth <number>`：控制 schema 展开深度，默认 `5`

## 注意事项

- 不要只生成接口目录，必须展开入参和响应结构体。
- 参数数量不等于字段结构，不能只写 `Params: 1`。
- `$ref` 必须解析到 `components.schemas`。
- 遇到递归引用要截断并标明“递归引用，已省略”。
- 文档过长是正常的，字段级 API 文档优先完整性。

## 参考

- [references/output-format.md](references/output-format.md)
- [templates/api-doc.example.md](templates/api-doc.example.md)
