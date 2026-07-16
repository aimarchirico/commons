#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const packageRoot = path.resolve(__dirname, '..');
const cwd = process.cwd();

fs.copyFileSync(
  path.join(packageRoot, 'CONTRIBUTING.md'),
  path.join(cwd, 'CONTRIBUTING.md'),
);
fs.cpSync(path.join(packageRoot, 'github'), path.join(cwd, '.github'), {
  recursive: true,
});
console.log('Materialized CONTRIBUTING.md and .github templates.');
