import {Linter} from 'eslint';
import {describe, expect, it} from 'vitest';
import tseslint from 'typescript-eslint';
import {defaultExportShape} from '../default-export-shape';

const linter = new Linter({configType: 'flat'});

const lint = (code: string) =>
  linter.verify(code, {
    languageOptions: {
      parser: tseslint.parser,
      sourceType: 'module',
      ecmaVersion: 2022,
    },
    plugins: {commons: {rules: {'default-export-shape': defaultExportShape}}},
    rules: {'commons/default-export-shape': 'error'},
  });

const messageIds = (code: string) =>
  lint(code).map(message => message.messageId);

describe('defaultExportShape', () => {
  it('flags an inline object literal', () => {
    expect(messageIds('export default {a: 1};\n')).toEqual([
      'inlineDefaultExport',
    ]);
  });

  it('flags an inline array literal', () => {
    expect(messageIds('export default [1, 2, 3];\n')).toEqual([
      'inlineDefaultExport',
    ]);
  });

  it('allows a call expression', () => {
    expect(messageIds('export default defineConfig({});\n')).toEqual([]);
  });

  it('flags a plain identifier', () => {
    expect(
      messageIds('const config = {a: 1};\nexport default config;\n'),
    ).toEqual(['inlineDefaultExport']);
  });

  it('allows a named function declaration', () => {
    expect(messageIds('export default function foo() {}\n')).toEqual([]);
  });

  it('allows a named class declaration', () => {
    expect(messageIds('export default class Foo {}\n')).toEqual([]);
  });
});
