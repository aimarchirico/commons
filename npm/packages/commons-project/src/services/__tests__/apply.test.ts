import fs from 'fs';
import os from 'os';
import path from 'path';
import {afterEach, beforeEach, describe, expect, it} from 'vitest';
import {applyDelete, applyMove, applyReplacement} from '../apply';
import type {Manifest} from '../../types/manifest';

let dir: string;
let originalCwd: string;

beforeEach(() => {
  dir = fs.mkdtempSync(path.join(os.tmpdir(), 'commons-project-apply-'));
  originalCwd = process.cwd();
  process.chdir(dir);
});

afterEach(() => {
  process.chdir(originalCwd);
  fs.rmSync(dir, {recursive: true, force: true});
});

const manifest: Manifest = {
  values: {name: {from: 'Template', to: 'My App'}},
};

describe('applyReplacement', () => {
  it('rewrites matched files and reports how many changed', async () => {
    fs.writeFileSync('a.txt', 'Hello Template!');
    fs.writeFileSync('b.txt', 'nothing to change here');

    const changed = await applyReplacement(
      {value: 'name', files: ['*.txt']},
      manifest,
    );

    expect(changed).toBe(1);
    expect(fs.readFileSync('a.txt', 'utf8')).toBe('Hello My App!');
    expect(fs.readFileSync('b.txt', 'utf8')).toBe('nothing to change here');
  });

  it('applies each requested transform variant', async () => {
    fs.writeFileSync('a.txt', 'Template template-kebab');
    const kebabManifest: Manifest = {
      values: {name: {from: 'Template', to: 'my-app'}},
    };
    const changed = await applyReplacement(
      {value: 'name', files: ['*.txt'], transforms: ['identity', 'kebab']},
      kebabManifest,
    );
    expect(changed).toBe(1);
    expect(fs.readFileSync('a.txt', 'utf8')).toBe('my-app template-kebab');
  });

  it('returns 0 without touching the filesystem when from equals to', async () => {
    fs.writeFileSync('a.txt', 'Same Same');
    const noopManifest: Manifest = {
      values: {name: {from: 'Same', to: 'Same'}},
    };
    const changed = await applyReplacement(
      {value: 'name', files: ['*.txt']},
      noopManifest,
    );
    expect(changed).toBe(0);
  });
});

describe('applyMove', () => {
  it('moves a file to its destination', () => {
    fs.mkdirSync('src', {recursive: true});
    fs.writeFileSync('src/file.txt', 'content');

    const result = applyMove(
      {from: 'src/file.txt', to: 'dest/file.txt'},
      {
        values: {},
      },
    );

    expect(result.moved).toBe(true);
    expect(fs.existsSync('dest/file.txt')).toBe(true);
    expect(fs.existsSync('src/file.txt')).toBe(false);
  });

  it('is a no-op when the source is missing', () => {
    const result = applyMove(
      {from: 'missing.txt', to: 'dest.txt'},
      {
        values: {},
      },
    );
    expect(result.moved).toBe(false);
    expect(fs.existsSync('dest.txt')).toBe(false);
  });

  it('is a no-op when from and to resolve to the same path', () => {
    fs.writeFileSync('same.txt', 'content');
    const result = applyMove(
      {from: 'same.txt', to: 'same.txt'},
      {
        values: {},
      },
    );
    expect(result.moved).toBe(false);
  });

  it('overwrites an existing destination', () => {
    fs.writeFileSync('from.txt', 'new');
    fs.writeFileSync('to.txt', 'old');
    const result = applyMove({from: 'from.txt', to: 'to.txt'}, {values: {}});
    expect(result.moved).toBe(true);
    expect(fs.readFileSync('to.txt', 'utf8')).toBe('new');
  });

  it('interpolates placeholders in from/to using manifest values', () => {
    fs.mkdirSync('pkg/com/template', {recursive: true});
    fs.writeFileSync('pkg/com/template/App.kt', 'content');
    const result = applyMove(
      {from: 'pkg/{{name.from|path}}', to: 'pkg/{{name.to|path}}'},
      {values: {name: {from: 'com.template', to: 'com.myapp'}}},
    );
    expect(result.moved).toBe(true);
    expect(fs.existsSync('pkg/com/myapp')).toBe(true);
  });
});

describe('applyDelete', () => {
  it('deletes an existing target', () => {
    fs.writeFileSync('gone.txt', 'bye');
    expect(applyDelete('gone.txt')).toBe('deleted');
    expect(fs.existsSync('gone.txt')).toBe(false);
  });

  it('skips a missing target', () => {
    expect(applyDelete('missing.txt')).toBe('skipped');
  });
});
