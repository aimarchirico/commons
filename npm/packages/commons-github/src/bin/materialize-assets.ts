#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Materialize all GitHub assets into the local .github directory.
 */
export function materializeAssets(): void {
  const packageRoot = path.resolve(__dirname, '..', '..');
  const cwd = process.cwd();
  const githubDir = path.join(cwd, '.github');

  fs.mkdirSync(githubDir, {recursive: true});
  fs.cpSync(path.join(packageRoot, 'src', 'assets', 'github'), githubDir, {
    recursive: true,
  });
  console.log('Materialized .github assets.');
}
