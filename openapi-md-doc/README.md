# OpenAPI Markdown Doc

`openapi-md-doc` 用于把 OpenAPI / Swagger 的 `api-docs` 地址或 JSON 文件转换成字段级 Markdown API 文档。

适用场景：

- 前端需要根据后端 `/v3/api-docs` 快速整理接口
- 需要完整入参和响应结构体
- 需要把接口文档保存为 Markdown，供后续联调和开发使用

## 使用方式

```bash
node scripts/generate-openapi-md.js \
  --input http://example.com/admin-app/v3/api-docs \
  --output docs/api/admin-app-v3-api-docs.md
```

也支持本地 JSON：

```bash
node scripts/generate-openapi-md.js \
  --input ./openapi.json \
  --output ./api-docs.md
```

## 输出内容

- 来源信息
- 分组概览
- 每个接口的方法、路径、摘要、operationId
- Parameters
- Request Body 字段结构
- Responses 字段结构

## 要求

- Node.js 18+
- 如果输入是 URL，需要当前环境可访问该地址
