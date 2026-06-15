#!/usr/bin/env node
/*
 * compile.js —— 知识库编译验证脚本（Karpathy 四层架构）
 * 设计原则：只「验证」，不「修正」。发现问题报告出来，由人工修复。
 * 用法：node compile.js
 * 退出码：有 [错误] 返回 1，否则返回 0（[警告] 不影响退出码）。
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
let errors = 0, warnings = 0;
const err = (m) => { console.error('  [错误] ' + m); errors++; };
const warn = (m) => { console.warn('  [警告] ' + m); warnings++; };
const ok = (m) => console.log('  [通过] ' + m);

// 递归收集所有 .md 文件（跳过 .git / node_modules）
function listMd(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['.git', 'node_modules'].includes(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) listMd(p, acc);
    else if (e.name.toLowerCase().endsWith('.md')) acc.push(p);
  }
  return acc;
}
const rel = (p) => path.relative(ROOT, p).replace(/\\/g, '/');

console.log('=== 1. 结构完整性检查 ===');
const requiredDirs = ['raw/notes', 'wiki/summaries', 'wiki/baselines', 'archive'];
for (const d of requiredDirs) {
  if (fs.existsSync(path.join(ROOT, d))) ok('目录存在: ' + d);
  else err('缺少必需目录: ' + d);
}

console.log('\n=== 2. raw/notes 命名规范检查 ===');
const notesDir = path.join(ROOT, 'raw/notes');
const tsPattern = /^.+-\d{8}-\d{4}-.+\.md$/; // {角色}-YYYYMMDD-HHMM-...
let noteCount = 0;
if (fs.existsSync(notesDir)) {
  for (const f of fs.readdirSync(notesDir)) {
    if (!f.toLowerCase().endsWith('.md') || f.startsWith('_')) continue; // 跳过说明文件
    noteCount++;
    if (!tsPattern.test(f)) warn(`命名不符合 {角色}-YYYYMMDD-HHMM-...: raw/notes/${f}`);
  }
}
ok(`raw/notes 中需求记录文件 ${noteCount} 个`);

console.log('\n=== 3. 双向链接有效性检查 ===');
const allMd = listMd(ROOT);
const basenames = new Set(allMd.map((p) => path.basename(p, '.md')));
const linkRe = /\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]/g;
let linkCount = 0;
for (const file of allMd) {
  const text = fs.readFileSync(file, 'utf8');
  let m;
  while ((m = linkRe.exec(text)) !== null) {
    linkCount++;
    const base = path.basename(m[1].trim(), '.md');
    if (!basenames.has(base)) warn(`断链: ${rel(file)} -> [[${m[1].trim()}]]`);
  }
}
ok(`扫描 ${allMd.length} 个 .md，双向链接 ${linkCount} 处`);

console.log('\n=== 4. 内容格式检查（代码块闭合） ===');
for (const file of allMd) {
  const text = fs.readFileSync(file, 'utf8');
  const fences = (text.match(/^```/gm) || []).length;
  if (fences % 2 !== 0) warn(`代码块未闭合（\`\`\` 数量为奇数）: ${rel(file)}`);
}
ok('代码块闭合检查完成');

console.log('\n=== 5. 基线一致性检查 ===');
const blDir = path.join(ROOT, 'wiki/baselines');
let blCount = 0;
if (fs.existsSync(blDir)) {
  for (const e of fs.readdirSync(blDir, { withFileTypes: true })) {
    if (!e.isDirectory()) continue;
    blCount++;
    if (!/^BL-\d{8}-\d{2}$/.test(e.name)) {
      warn(`基线目录名不符合 BL-YYYYMMDD-NN: ${e.name}`);
      continue;
    }
    const files = fs.readdirSync(path.join(blDir, e.name));
    if (!files.some((f) => /SRS.*正式/.test(f)))
      warn(`基线 ${e.name} 缺少 SRS 正式版文件`);
  }
}
ok(`已创立基线 ${blCount} 个`);

console.log('\n================ 编译结果 ================');
console.log(`错误 ${errors} 个，警告 ${warnings} 个`);
if (errors === 0) console.log('知识库结构校验通过 ✔');
process.exit(errors > 0 ? 1 : 0);
