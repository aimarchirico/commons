#!/usr/bin/env node
const { spawnSync } = require('child_process');

let markdownlintBin;
try {
  markdownlintBin = require.resolve('markdownlint-cli2/markdownlint-cli2.js');
} catch (e) {
  markdownlintBin = require.resolve('markdownlint-cli2');
}

const result = spawnSync(process.execPath, [markdownlintBin, ...process.argv.slice(2)], {
  stdio: 'inherit',
});
process.exit(result.status ?? 0);
