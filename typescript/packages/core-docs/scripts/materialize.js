#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const source = path.resolve(__dirname, '..');
const target = process.cwd();

fs.copyFileSync(
  path.join(source, 'CONTRIBUTING.md'),
  path.join(target, 'CONTRIBUTING.md'),
);
fs.cpSync(path.join(source, 'github'), path.join(target, '.github'), {
  recursive: true,
});

console.log('Materialized CONTRIBUTING.md and .github templates.');
