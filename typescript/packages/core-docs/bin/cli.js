#!/usr/bin/env node
'use strict';

const {execFileSync} = require('child_process');
const fs = require('fs');
const path = require('path');

const packageRoot = path.resolve(__dirname, '..');
const cwd = process.cwd();
const command = process.argv[2];

/**
 * markdownlint-cli2's package entry doubles as its CLI executable.
 * @param {string[]} args
 */
function runMarkdownlint(args) {
  const bin = require.resolve('markdownlint-cli2', {paths: [cwd, packageRoot]});
  execFileSync(process.execPath, [bin, ...args], {stdio: 'inherit', cwd});
}

function init() {
  fs.copyFileSync(
    path.join(packageRoot, 'CONTRIBUTING.md'),
    path.join(cwd, 'CONTRIBUTING.md'),
  );
  fs.cpSync(path.join(packageRoot, 'github'), path.join(cwd, '.github'), {
    recursive: true,
  });
  console.log('Materialized CONTRIBUTING.md and .github templates.');
}

switch (command) {
  case 'check':
    runMarkdownlint([]);
    break;
  case 'fix':
    runMarkdownlint(['--fix']);
    break;
  case 'init':
    init();
    break;
  default:
    console.error(
      'core-docs: unknown command "' +
        (command || '') +
        '". Expected "check", "fix", or "init".',
    );
    process.exit(1);
}
