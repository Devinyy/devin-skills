#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

function usage() {
  console.error(`Usage:
  node scripts/generate-openapi-md.js --input <url-or-json-file> --output <output.md> [--title <title>] [--source <source>] [--max-depth <number>]

Examples:
  node scripts/generate-openapi-md.js --input http://example.com/v3/api-docs --output docs/api/api-docs.md
  node scripts/generate-openapi-md.js --input ./openapi.json --output ./api-docs.md
`);
  process.exit(1);
}

function parseArgs(argv) {
  const args = { maxDepth: 5 };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--input') args.input = argv[++i];
    else if (arg === '--output') args.output = argv[++i];
    else if (arg === '--title') args.title = argv[++i];
    else if (arg === '--source') args.source = argv[++i];
    else if (arg === '--max-depth') args.maxDepth = Number(argv[++i]);
    else usage();
  }
  if (!args.input || !args.output) usage();
  if (!Number.isFinite(args.maxDepth) || args.maxDepth < 1) args.maxDepth = 5;
  return args;
}

function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https:') ? https : http;
    const req = client.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        fetchUrl(new URL(res.headers.location, url).toString()).then(resolve, reject);
        return;
      }
      if (res.statusCode < 200 || res.statusCode >= 300) {
        reject(new Error(`GET ${url} failed with status ${res.statusCode}`));
        return;
      }
      let data = '';
      res.setEncoding('utf8');
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
  });
}

function isUrl(input) {
  return /^https?:\/\//i.test(input);
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function esc(value) {
  return String(value ?? '')
    .replace(/\|/g, '\\|')
    .replace(/\r?\n/g, ' ')
    .trim();
}

function refName(ref) {
  return ref ? ref.replace('#/components/schemas/', '') : '';
}

function makeRenderer(spec, options) {
  const schemas = spec.components?.schemas || {};
  const maxDepth = options.maxDepth || 5;

  function resolve(schema) {
    if (!schema) return schema;
    if (schema.$ref) return schemas[refName(schema.$ref)] || schema;
    return schema;
  }

  function typeName(schema) {
    if (!schema) return '-';
    if (schema.$ref) return refName(schema.$ref);
    if (schema.oneOf) return schema.oneOf.map(typeName).join(' | ');
    if (schema.anyOf) return schema.anyOf.map(typeName).join(' | ');
    if (schema.allOf) return schema.allOf.map(typeName).join(' & ');
    if (schema.type === 'array') return `Array<${typeName(schema.items)}>`;
    if (schema.type) return schema.type;
    if (schema.properties) return 'object';
    return '-';
  }

  function schemaRows(schema, prefix = '', depth = 0, seen = new Set(), includeSelf = true) {
    if (!schema || depth > maxDepth) return [];
    const originalType = typeName(schema);

    if (schema.$ref) {
      const name = refName(schema.$ref);
      if (seen.has(name)) return [[prefix || name, name, '', '', '递归引用，已省略']];
      seen = new Set(seen);
      seen.add(name);
      schema = resolve(schema);
    }

    if (schema.allOf) {
      return schema.allOf.flatMap(item => schemaRows(item, prefix, depth, seen, includeSelf));
    }

    if (schema.oneOf || schema.anyOf) {
      const items = schema.oneOf || schema.anyOf;
      const rows = includeSelf
        ? [[prefix || '-', originalType, '', '', schema.description || '多类型结构']]
        : [];
      return rows.concat(
        items.flatMap((item, index) => schemaRows(item, `${prefix || 'value'}[${index}]`, depth + 1, seen, true))
      );
    }

    if (schema.type === 'array') {
      const rows = includeSelf
        ? [[prefix || '[]', typeName(schema), '', '', schema.description || '']]
        : [];
      return rows.concat(schemaRows(schema.items, `${prefix || 'items'}[]`, depth + 1, seen, true));
    }

    const props = schema.properties || {};
    const required = new Set(schema.required || []);

    if (!Object.keys(props).length) {
      return prefix ? [[prefix, originalType, '', schema.default ?? '', schema.description || '']] : [];
    }

    const rows = [];
    for (const [key, prop] of Object.entries(props)) {
      const name = prefix ? `${prefix}.${key}` : key;
      rows.push([
        name,
        typeName(prop),
        required.has(key) ? 'Y' : 'N',
        prop.default ?? '',
        prop.description || '',
      ]);

      const resolved = resolve(prop);
      if ((prop.$ref || resolved?.properties || resolved?.type === 'array') && depth < maxDepth - 1) {
        rows.push(...schemaRows(prop, name, depth + 1, seen, false));
      }
    }
    return rows;
  }

  function schemaTable(schema) {
    const rows = schemaRows(schema);
    if (!rows.length) return '-';
    return [
      '| 字段 | 类型 | 必填 | 默认值 | 说明 |',
      '| --- | --- | --- | --- | --- |',
      ...rows.map(row => `| ${esc(row[0])} | ${esc(row[1])} | ${esc(row[2])} | ${esc(row[3])} | ${esc(row[4])} |`),
    ].join('\n');
  }

  function pickSchemaFromContent(content) {
    if (!content) return null;
    const preferred = content['application/json'] || content['*/*'] || Object.values(content)[0];
    return preferred?.schema || null;
  }

  function paramTable(parameters = []) {
    if (!parameters.length) return '-';
    const rows = parameters.map(param => (
      `| ${esc(param.name)} | ${esc(param.in)} | ${param.required ? 'Y' : 'N'} | ${esc(typeName(param.schema))} | ${esc(param.description || '')} |`
    ));
    return [
      '| 参数 | 位置 | 必填 | 类型 | 说明 |',
      '| --- | --- | --- | --- | --- |',
      ...rows,
    ].join('\n');
  }

  function requestBody(operation) {
    const schema = pickSchemaFromContent(operation.requestBody?.content);
    if (!schema) return '-';
    return `Schema: \`${esc(typeName(schema))}\`\n\n${schemaTable(schema)}`;
  }

  function responses(operation) {
    const res = operation.responses || {};
    const parts = [];
    for (const [code, item] of Object.entries(res)) {
      const schema = pickSchemaFromContent(item.content);
      parts.push(`#### ${code} ${item.description || ''}`.trim());
      if (schema) parts.push(`Schema: \`${esc(typeName(schema))}\`\n\n${schemaTable(schema)}`);
      else parts.push('-');
    }
    return parts.join('\n\n');
  }

  return { typeName, paramTable, requestBody, responses };
}

function collectGroups(spec) {
  const groups = new Map();
  for (const [apiPath, pathItem] of Object.entries(spec.paths || {})) {
    for (const [method, operation] of Object.entries(pathItem)) {
      if (!['get', 'post', 'put', 'delete', 'patch'].includes(method)) continue;
      const tag = operation.tags?.[0] || '未分组';
      if (!groups.has(tag)) groups.set(tag, []);
      groups.get(tag).push({ method: method.toUpperCase(), path: apiPath, operation });
    }
  }
  return Array.from(groups.entries());
}

function renderMarkdown(spec, args) {
  const groups = collectGroups(spec);
  const sortedByName = [...groups].sort((a, b) => a[0].localeCompare(b[0], 'zh'));
  const sortedByCount = [...groups].sort((a, b) => b[1].length - a[1].length || a[0].localeCompare(b[0], 'zh'));
  const schemas = spec.components?.schemas || {};
  const renderer = makeRenderer(spec, args);
  const title = args.title || `${spec.info?.title || 'OpenAPI'} API 接口文档`;
  const source = args.source || args.input;

  let md = '';
  md += `# ${title}\n\n`;
  md += '## 来源\n\n';
  md += `- 来源：\`${source}\`\n`;
  md += `- 协议：OpenAPI \`${spec.openapi || spec.swagger || '-'}\`\n`;
  md += `- 标题：\`${spec.info?.title || '-'}\`\n`;
  md += `- 版本：\`${spec.info?.version || '-'}\`\n`;
  md += `- 接口路径数：\`${Object.keys(spec.paths || {}).length}\`\n`;
  md += `- 接口分组数：\`${groups.length}\`\n`;
  md += `- Schema 数：\`${Object.keys(schemas).length}\`\n`;
  md += `- 生成时间：\`${today()}\`\n\n`;
  md += '## 说明\n\n';
  md += '本文档由 OpenAPI JSON 自动整理而来，用于前端开发快速查阅接口。每个接口包含基础信息、Path/Query/Header 参数、Request Body 结构与 Response 结构。\n\n';
  md += '## 分组概览\n\n';
  md += '| 分组 | 接口数 |\n| --- | ---: |\n';
  for (const [tag, operations] of sortedByCount) md += `| ${esc(tag)} | ${operations.length} |\n`;
  md += '\n';

  for (const [tag, operations] of sortedByName) {
    md += `## ${tag}\n\n`;
    const sortedOps = operations.sort((a, b) => a.path.localeCompare(b.path) || a.method.localeCompare(b.method));
    for (const { method, path: apiPath, operation } of sortedOps) {
      md += `### ${method} ${apiPath}\n\n`;
      md += `- 名称：${operation.summary || '-'}\n`;
      md += `- OperationId：\`${operation.operationId || '-'}\`\n`;
      if (operation.description && operation.description !== operation.summary) md += `- 描述：${operation.description}\n`;
      md += '\n#### Parameters\n\n';
      md += renderer.paramTable(operation.parameters || []) + '\n\n';
      md += '#### Request Body\n\n';
      md += renderer.requestBody(operation) + '\n\n';
      md += '#### Responses\n\n';
      md += renderer.responses(operation) + '\n\n';
    }
  }
  return md;
}

async function main() {
  const args = parseArgs(process.argv);
  const sourceText = isUrl(args.input)
    ? await fetchUrl(args.input)
    : fs.readFileSync(path.resolve(args.input), 'utf8');
  const spec = JSON.parse(sourceText);
  const markdown = renderMarkdown(spec, args);
  const outputPath = path.resolve(args.output);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, markdown);
  console.log(JSON.stringify({
    output: outputPath,
    pathCount: Object.keys(spec.paths || {}).length,
    groupCount: collectGroups(spec).length,
    schemaCount: Object.keys(spec.components?.schemas || {}).length,
    lineCount: markdown.split('\n').length,
  }, null, 2));
}

main().catch(error => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
