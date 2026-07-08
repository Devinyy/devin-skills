# Output Format

## 文档结构

```markdown
# <Title>

## 来源

- 地址或文件
- OpenAPI / Swagger 版本
- 标题
- 版本
- 接口路径数
- 接口分组数
- Schema 数
- 生成时间

## 说明

## 分组概览

## <Tag>

### <METHOD> <PATH>

- 名称
- OperationId
- 描述

#### Parameters

#### Request Body

#### Responses
```

## 字段表结构

```markdown
| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| data.list[].id | string | N |  | 主键 |
```

## 展开规则

- `$ref` 展开到 `components.schemas`
- `array` 展开为 `字段[]`
- 嵌套对象展开为 `parent.child`
- 响应统一保留外层 `code / message / data`
- 递归引用必须截断，避免无限展开

## 验收标准

- 至少抽查一个有 request body 的接口，确认请求字段已展开
- 至少抽查一个有 data 对象的响应，确认响应字段已展开
- 分组数量与 OpenAPI tag 或 operation tags 对齐
