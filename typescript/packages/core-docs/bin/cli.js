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

/**
 * Resolve and run the commitlint CLI, forwarding any extra args
 * (e.g. --from/--to) through to it.
 * @param {string[]} args
 */
function runCommitlint(args) {
  const bin = require.resolve('@commitlint/cli/cli.js', {
    paths: [cwd, packageRoot],
  });
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
  fs.writeFileSync(
    path.join(cwd, 'commitlint.config.js'),
    "module.exports = {extends: ['@aimarchirico/core-docs/commitlint']};\n",
  );
  console.log(
    'Materialized CONTRIBUTING.md, .github templates, and commitlint.config.js.',
  );
}

switch (command) {
  case 'check':
    runMarkdownlint([]);
    break;
  case 'fix':
    runMarkdownlint(['--fix']);
    break;
  case 'commitlint':
    runCommitlint(process.argv.slice(3));
    break;
  case 'init':
    init();
    break;
  default:
    console.error(
      'core-docs: unknown command "' +
        (command || '') +
        '". Expected "check", "fix", "commitlint", or "init".',
    );
    process.exit(1);
}
