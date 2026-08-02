#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Materialize GitHub template files into the local .github directory.
 */
export function materializeTemplates(): void {
  const packageRoot = path.resolve(__dirname, '..', '..');
  const cwd = process.cwd();
  const githubDir = path.join(cwd, '.github');

  fs.mkdirSync(githubDir, {recursive: true});
  fs.copyFileSync(
    path.join(packageRoot, 'src', 'assets', 'CONTRIBUTING.md'),
    path.join(githubDir, 'CONTRIBUTING.md'),
  );
  fs.cpSync(path.join(packageRoot, 'src', 'assets', 'github'), githubDir, {
    recursive: true,
  });
  console.log('Materialized CONTRIBUTING.md and .github templates.');
}

if (!process.env.VITEST) {
  materializeTemplates();
}
