# Publish Checklist

## 文件结构

- `SKILL.md`
- `README.md`
- `agents/openai.yaml`
- `references/output-format.md`
- `templates/api-doc.example.md`
- `scripts/generate-openapi-md.js`

## 功能检查

- 支持 URL 输入
- 支持本地 JSON 输入
- 能输出 Markdown
- 能展开 request body schema
- 能展开 response schema
- 能处理 `$ref`
- 能处理 array / object / nested object
- 能截断递归引用

## 安全检查

- 不提交真实内网 token
- 不提交下载后的私有 OpenAPI JSON
- 不在模板里写真实生产域名

## 验收命令

```bash
node scripts/generate-openapi-md.js --input ./openapi.json --output ./api-docs.md
```
