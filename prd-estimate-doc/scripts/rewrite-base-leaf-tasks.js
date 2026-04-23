#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

function usage() {
  console.error(
    'Usage: node rewrite-base-leaf-tasks.js --config <config.json> [--apply]\n' +
    'Config schema:\n' +
    '{\n' +
    '  "baseToken": "...",\n' +
    '  "merchantTableId": "...",\n' +
    '  "opsTableId": "...",\n' +
    '  "merchantRecordsPath": "...json",\n' +
    '  "opsRecordsPath": "...json",\n' +
    '  "merchantTasks": [...],\n' +
    '  "opsTasks": [...]\n' +
    '}'
  );
  process.exit(1);
}

function parseArgs(argv) {
  const args = { apply: false };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--apply') {
      args.apply = true;
      continue;
    }
    if (arg === '--config') {
      args.configPath = argv[++i];
      continue;
    }
    usage();
  }
  if (!args.configPath) usage();
  return args;
}

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function collectChildIds(raw) {
  const fields = raw.data.fields;
  const rows = raw.data.data;
  const ids = raw.data.record_id_list;
  const idxParent = fields.indexOf('Parent items');
  const idxHours = fields.indexOf('工时(h)');
  const childIds = [];
  const rootIds = [];
  rows.forEach((row, i) => {
    const hasParent = !!(row[idxParent] && row[idxParent][0] && row[idxParent][0].id);
    if (hasParent) childIds.push(ids[i]);
    else if (row[idxHours] != null) rootIds.push(ids[i]);
  });
  return { childIds, rootIds };
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function runLark(args) {
  let lastErr;
  for (let i = 0; i < 6; i++) {
    try {
      cp.execFileSync('lark-cli', args, { stdio: 'inherit' });
      return;
    } catch (err) {
      lastErr = err;
      const msg = String(err && err.message || err);
      if (!msg.includes('limited') && !msg.includes('429')) throw err;
      sleep(1200 * (i + 1));
    }
  }
  throw lastErr;
}

function buildAssignments(ids, tasks) {
  return tasks.map((task, idx) => ({
    recordId: ids[idx],
    payload: {
      '主模块': task.module,
      '优先级': task.priority,
      'Parent items': [{ id: task.parent }],
      '任务': task.task,
      '任务状态': task.status || '待开始',
      '备注': task.remark,
      '工时(h)': task.hours,
      '阶段': task.stage,
      '任务评审': task.review || '待评审'
    }
  }));
}

function applyAssignments(baseToken, tableId, assignments) {
  for (const item of assignments) {
    runLark([
      'base', '+record-upsert',
      '--base-token', baseToken,
      '--table-id', tableId,
      '--record-id', item.recordId,
      '--json', JSON.stringify(item.payload),
    ]);
  }
}

function main() {
  const args = parseArgs(process.argv);
  const configPath = path.resolve(args.configPath);
  const config = loadJson(configPath);

  const merchantRaw = loadJson(path.resolve(config.merchantRecordsPath));
  const opsRaw = loadJson(path.resolve(config.opsRecordsPath));
  const merchant = collectChildIds(merchantRaw);
  const ops = collectChildIds(opsRaw);

  if (merchant.childIds.length !== config.merchantTasks.length) {
    throw new Error(`merchant child count mismatch: ids=${merchant.childIds.length}, tasks=${config.merchantTasks.length}`);
  }
  if (ops.childIds.length !== config.opsTasks.length) {
    throw new Error(`ops child count mismatch: ids=${ops.childIds.length}, tasks=${config.opsTasks.length}`);
  }

  const merchantAssignments = buildAssignments(merchant.childIds, config.merchantTasks);
  const opsAssignments = buildAssignments(ops.childIds, config.opsTasks);

  if (!args.apply) {
    console.log(JSON.stringify({
      merchantChildIds: merchant.childIds,
      merchantRootIds: merchant.rootIds,
      opsChildIds: ops.childIds,
      opsRootIds: ops.rootIds,
      merchantAssignments: merchantAssignments.length,
      opsAssignments: opsAssignments.length,
    }, null, 2));
    return;
  }

  runLark([
    'base', '+record-batch-update',
    '--base-token', config.baseToken,
    '--table-id', config.merchantTableId,
    '--json', JSON.stringify({ record_id_list: merchant.rootIds, patch: { '工时(h)': null } }),
  ]);
  runLark([
    'base', '+record-batch-update',
    '--base-token', config.baseToken,
    '--table-id', config.opsTableId,
    '--json', JSON.stringify({ record_id_list: ops.rootIds, patch: { '工时(h)': null } }),
  ]);

  applyAssignments(config.baseToken, config.merchantTableId, merchantAssignments);
  applyAssignments(config.baseToken, config.opsTableId, opsAssignments);
}

main();
