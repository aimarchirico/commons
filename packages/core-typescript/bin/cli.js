#!/usr/bin/env node
const { spawnSync } = require('child_process');

let tscBin;
try {
  tscBin = require.resolve('typescript/bin/tsc');
} catch (e) {
  tscBin = require.resolve('typescript');
}

const result = spawnSync(process.execPath, [tscBin, ...process.argv.slice(2)], {
  stdio: 'inherit',
});
process.exit(result.status ?? 0);
