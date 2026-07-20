# Base Sync

## 目的

本文件说明什么时候应该把 PRD 估时结果同步到飞书 Base，以及什么时候应该改用内置脚本批量写入。

## 两种方式

### 1. 手动 / 原子写入

适合：
- 只新增少量字段
- 只改少量记录
- 还在边做边确认任务口径

做法：
- 先读表结构
- 再按字段逐条写入
- 每一步都回读确认

### 2. 脚本批量写入

适合：
- 明细表已经形成父任务 + 叶子任务结构
- 需要重写几十条记录
- 任务命名、阶段、优先级口径已经稳定

做法：
- 先导出或读取当前表记录
- 准备配置文件，而不是在脚本里写死项目参数
- 先跑只读预览，再执行真正写入

## 内置脚本

### `scripts/rewrite-base-leaf-tasks.js`

用途：
- 读取已导出的 Base 记录 JSON
- 识别父任务和子任务
- 清空父任务工时
- 按预定义叶子任务清单重写工时、阶段、备注等字段

配置模板：
- `templates/rewrite-base-config.example.json`

执行方式：

```bash
node scripts/rewrite-base-leaf-tasks.js --config ./rewrite-base-config.json
node scripts/rewrite-base-leaf-tasks.js --config ./rewrite-base-config.json --apply
```

说明：
- 不带 `--apply` 时只做预览
- 带 `--apply` 时才真正回写 Base

### `scripts/apply-ai-schedule-fields.js`

用途：
- 在两张明细表中自动补 `AI直接实现`、`执行方式`、`执行波次`
- 支持先建字段，再按规则批量写记录

配置模板：
- `templates/ai-schedule-config.example.json`

执行方式：

```bash
node scripts/apply-ai-schedule-fields.js --config ./ai-schedule-config.json
```

说明：
- 该脚本会先检查并补齐字段，再批量回写叶子任务
- 默认按阶段和任务名推导 `AI直接实现 / 执行方式 / 执行波次`

## 使用原则

- 脚本只在任务口径已经定死时使用
- 任何脚本执行前都要先回读当前表结构
- `base token`、`table id`、任务映射、波次规则都应视为项目级配置，不要盲目复用到别的表
- 执行后必须回读检查：
  - 父任务工时是否为空
  - 叶子任务是否都有工时
  - `开发 / 联调 / 总计` 汇总是否符合预期

## 当前沉淀内容

这两个脚本来自 `O2 商品中心` 的实际操作过程，已验证过以下流程：
- 把明细表切到叶子任务工时口径
- 把系统设置联调任务补入估时表
- 给叶子任务补 `AI直接实现 / 执行方式 / 执行波次`
