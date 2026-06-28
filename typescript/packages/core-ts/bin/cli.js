#!/usr/bin/env node
'use strict';

const {execFileSync} = require('child_process');
const path = require('path');

const cwd = process.cwd();
const isCI = Boolean(process.env.CI);
const command = process.argv[2];
const target = process.argv[3] || 'src';

/**
 * Resolve a dependency's declared executable from the consuming project.
 * @param {string} name
 * @param {string} binName
 * @returns {string}
 */
function resolveBin(name, binName) {
  const manifestPath = require.resolve(name + '/package.json', {paths: [cwd]});
  const manifest = require(manifestPath);
  const bin =
    typeof manifest.bin === 'string' ? manifest.bin : manifest.bin[binName];
  return path.join(path.dirname(manifestPath), bin);
}

/**
 * @param {string} bin
 * @param {string[]} args
 */
function runNode(bin, args) {
  execFileSync(process.execPath, [bin, ...args], {stdio: 'inherit', cwd});
}

/**
 * @param {string[]} extra
 */
function runEslint(extra) {
  // --no-error-on-unmatched-pattern keeps empty/all-ignored globs from failing.
  runNode(resolveBin('eslint', 'eslint'), [
    target,
    '--no-error-on-unmatched-pattern',
    ...extra,
  ]);
}

function runTsc() {
  runNode(resolveBin('typescript', 'tsc'), ['--noEmit']);
}

switch (command) {
  case 'check':
    // CI is strict: warnings fail the build.
    runEslint(isCI ? ['--max-warnings', '0'] : []);
    runTsc();
    break;
  case 'fix':
    runEslint(['--fix']);
    break;
  default:
    console.error(
      'core-ts: unknown command "' +
        (command || '') +
        '". Expected "check" or "fix".',
    );
    process.exit(1);
}
