#!/usr/bin/env node
const { spawnSync } = require('child_process');

let eslintBin;
try {
  eslintBin = require.resolve('eslint/bin/eslint.js');
} catch (e) {
  // Fallback for some environments or custom installations
  eslintBin = require.resolve('eslint');
}

const result = spawnSync(process.execPath, [eslintBin, ...process.argv.slice(2)], {
  stdio: 'inherit',
});
process.exit(result.status ?? 0);
