# Example Smoke Case Shape

This reference is based on a product-center smoke workbook example. Use it only as a shape example, not as fixed domain logic.

Common columns:

- 测试编号
- 标题
- 目录
- 负责人
- 前置条件
- 操作步骤
- 预期结果
- 关联需求
- 优先级
- 类型
- 标签

Example normalized case:

```json
{
  "caseId": "pro_008",
  "title": "商品价格管理_新增规则_商品",
  "modulePath": "运营后台/商品/商品价格管理",
  "precondition": "运营人员已登录系统，进入价格规则管理页面",
  "steps": [
    "点击「新增规则」按钮",
    "填写规则名称，选择加价维度、加价方式和加价值",
    "选择生效商品",
    "点击「保存」按钮"
  ],
  "expected": [
    "规则创建成功，状态为生效中",
    "列表显示新创建的规则",
    "落库 target_type 正确"
  ],
  "priority": "P0",
  "tags": "冒烟测试"
}
```

Useful execution split:

- UI path: navigation, form input, selection, submit, inline validation.
- API-assisted verification: created ID, persisted dimension/method/value/targets, status.
- Report: case result, request/response evidence, created data, known issues.
