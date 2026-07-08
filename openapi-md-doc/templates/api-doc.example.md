# Example API 文档

## 来源

- 地址：`http://example.com/v3/api-docs`
- 协议：OpenAPI `3.1.0`
- 标题：`OpenAPI definition`
- 版本：`v0`
- 接口路径数：`10`
- 接口分组数：`2`
- Schema 数：`20`

## 示例分组

### POST /example/login

- 名称：登录
- OperationId：`login`

#### Parameters

-

#### Request Body

Schema: `LoginRequest`

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| account | string | Y |  | 账号 |
| password | string | Y |  | 密码 |

#### Responses

#### 200 OK

Schema: `ApiResultLoginVO`

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| code | integer | N | 0 | 状态码 |
| message | string | N | Success | 提示 |
| data | LoginVO | N |  | 登录数据 |
| data.access_token | string | N |  | access token |
