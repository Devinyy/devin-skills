#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

function usage() {
  console.error(
    'Usage: node apply-ai-schedule-fields.js --config <config.json>\n' +
    'Config schema:\n' +
    '{\n' +
    '  "baseToken": "...",\n' +
    '  "merchantTableId": "...",\n' +
    '  "opsTableId": "...",\n' +
    '  "summaryTableId": "...",\n' +
    '  "wave1Serial": ["任务A"],\n' +
    '  "wave1Parallel": ["任务B"],\n' +
    '  "wave3Serial": ["任务C"]\n' +
    '}'
  );
  process.exit(1);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
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

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function run(args, expectJson = true) {
  let lastErr;
  for (let i = 0; i < 6; i++) {
    try {
      const out = cp.execFileSync('lark-cli', args, {
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      return expectJson ? JSON.parse(out) : out;
    } catch (err) {
      lastErr = err;
      const stderr = String(err.stderr || '');
      const stdout = String(err.stdout || '');
      const msg = `${stderr}\n${stdout}\n${err.message}`;
      if (!msg.includes('limited') && !msg.includes('429')) throw err;
      sleep(1200 * (i + 1));
    }
  }
  throw lastErr;
}

function fieldList(baseToken, tableId) {
  return run(['base', '+field-list', '--base-token', baseToken, '--table-id', tableId]).data.fields;
}

function fieldCreate(baseToken, tableId, payload) {
  return run([
    'base', '+field-create',
    '--base-token', baseToken,
    '--table-id', tableId,
    '--json', JSON.stringify(payload),
  ]);
}

function recordList(baseToken, tableId) {
  return run([
    'base', '+record-list',
    '--base-token', baseToken,
    '--table-id', tableId,
    '--offset', '0',
    '--limit', '200',
  ]).data;
}

function recordUpsert(baseToken, tableId, recordId, payload) {
  return run([
    'base', '+record-upsert',
    '--base-token', baseToken,
    '--table-id', tableId,
    '--record-id', recordId,
    '--json', JSON.stringify(payload),
  ]);
}

const NEW_FIELDS = [
  { name: 'AI直接实现', type: 'checkbox' },
  {
    name: '执行方式',
    type: 'select',
    multiple: false,
    options: [
      { name: '可并行', hue: 'Blue', lightness: 'Lighter' },
      { name: '必须串行', hue: 'Orange', lightness: 'Lighter' },
    ],
  },
  { name: '执行波次', type: 'number' },
];

function computeAi(stage, task) {
  if (stage === '开发') return true;
  if (stage === '联调/自测') return !task.includes('联调');
  if (stage === '联调与全链路自测') return true;
  return null;
}

function computeExec(stage, task, rules) {
  if (stage === '联调/自测') return { mode: '必须串行', wave: 4 };
  if (stage === '联调与全链路自测') return { mode: '必须串行', wave: 5 };
  if (rules.wave1Serial.has(task)) return { mode: '必须串行', wave: 1 };
  if (rules.wave1Parallel.has(task)) return { mode: '可并行', wave: 1 };
  if (rules.wave3Serial.has(task)) return { mode: '必须串行', wave: 3 };
  return { mode: '可并行', wave: 2 };
}

function ensureFields(baseToken, tableId) {
  const existing = new Map(fieldList(baseToken, tableId).map((f) => [f.name, f]));
  for (const field of NEW_FIELDS) {
    if (!existing.has(field.name)) fieldCreate(baseToken, tableId, field);
  }
}

function updateLeafRows(baseToken, tableId, rules) {
  const data = recordList(baseToken, tableId);
  const idx = Object.fromEntries(data.fields.map((name, i) => [name, i]));
  let count = 0;
  for (let i = 0; i < data.data.length; i++) {
    const row = data.data[i];
    const parent = row[idx['Parent items']];
    if (!(parent && parent[0] && parent[0].id)) continue;
    const task = row[idx['任务']];
    const stageArr = row[idx['阶段']];
    const stage = stageArr && stageArr[0];
    const exec = computeExec(stage, task, rules);
    recordUpsert(baseToken, tableId, data.record_id_list[i], {
      'AI直接实现': computeAi(stage, task),
      '执行方式': exec.mode,
      '执行波次': exec.wave,
    });
    count += 1;
  }
  return count;
}

function verify(baseToken, tableId) {
  const data = recordList(baseToken, tableId);
  const idx = Object.fromEntries(data.fields.map((name, i) => [name, i]));
  const issues = [];
  for (let i = 0; i < data.data.length; i++) {
    const row = data.data[i];
    const parent = row[idx['Parent items']];
    if (!(parent && parent[0] && parent[0].id)) continue;
    if (row[idx['AI直接实现']] == null || row[idx['执行方式']] == null || row[idx['执行波次']] == null) {
      issues.push(data.record_id_list[i]);
    }
  }
  return issues;
}

function main() {
  const args = parseArgs(process.argv);
  const config = loadJson(path.resolve(args.configPath));
  const rules = {
    wave1Serial: new Set(config.wave1Serial || []),
    wave1Parallel: new Set(config.wave1Parallel || []),
    wave3Serial: new Set(config.wave3Serial || []),
  };

  ensureFields(config.baseToken, config.merchantTableId);
  ensureFields(config.baseToken, config.opsTableId);

  const merchantUpdated = updateLeafRows(config.baseToken, config.merchantTableId, rules);
  const opsUpdated = updateLeafRows(config.baseToken, config.opsTableId, rules);
  const merchantIssues = verify(config.baseToken, config.merchantTableId);
  const opsIssues = verify(config.baseToken, config.opsTableId);

  console.log(JSON.stringify({ merchantUpdated, opsUpdated, merchantIssues, opsIssues }, null, 2));
}

main();
