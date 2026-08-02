import {Linter} from 'eslint';
import {describe, expect, it} from 'vitest';
import tseslint from 'typescript-eslint';
import {publicJSDocOnly} from '../comments';

const linter = new Linter({configType: 'flat'});

function lint(code: string) {
  return linter.verify(code, {
    languageOptions: {
      parser: tseslint.parser,
      sourceType: 'module',
      ecmaVersion: 2022,
    },
    linterOptions: {reportUnusedDisableDirectives: false},
    plugins: {commons: {rules: {'public-jsdoc-only': publicJSDocOnly}}},
    rules: {'commons/public-jsdoc-only': 'error'},
  });
}

function messageIds(code: string) {
  return lint(code).map(message => message.messageId);
}

describe('publicJSDocOnly', () => {
  it('flags a plain line comment', () => {
    expect(messageIds('// hello\nexport const a = 1;\n')).toEqual([
      'nonJSDocComment',
    ]);
  });

  it('flags a plain block comment', () => {
    expect(messageIds('/* hello */\nexport const a = 1;\n')).toEqual([
      'nonJSDocComment',
    ]);
  });

  it('flags an orphaned JSDoc block', () => {
    expect(messageIds('/**\n * orphan\n */\n1 + 1;\n')).toEqual([
      'orphanedJSDoc',
    ]);
  });

  it('flags a JSDoc block on a non-exported function', () => {
    expect(
      messageIds('/**\n * Internal.\n */\nfunction helper() {}\n'),
    ).toEqual(['nonPublicJSDoc']);
  });

  it('allows a JSDoc block on an exported function', () => {
    expect(
      messageIds('/**\n * Does a thing.\n */\nexport function doThing() {}\n'),
    ).toEqual([]);
  });

  it('allows a JSDoc block on an exported const arrow function', () => {
    expect(
      messageIds('/**\n * Arrow.\n */\nexport const fn = () => {};\n'),
    ).toEqual([]);
  });

  it('allows a JSDoc block on an exported default call expression', () => {
    expect(
      messageIds('/**\n * Config.\n */\nexport default defineConfig({});\n'),
    ).toEqual([]);
  });

  it('allows a JSDoc block on exported type-only declarations', () => {
    const code = [
      '/**',
      ' * Interface.',
      ' */',
      'export interface Foo {',
      '  bar: string;',
      '}',
      '',
      '/**',
      ' * Alias.',
      ' */',
      'export type Bar = string;',
      '',
      '/**',
      ' * Enum.',
      ' */',
      'export enum Baz {',
      '  A,',
      '}',
      '',
    ].join('\n');
    expect(messageIds(code)).toEqual([]);
  });

  it('flags a JSDoc block on a private method or field', () => {
    const code = [
      '/**',
      ' * A widget.',
      ' */',
      'export class Widget {',
      '  /**',
      '   * Public method.',
      '   */',
      '  method() {}',
      '',
      '  /**',
      '   * Private method.',
      '   */',
      '  private helper() {}',
      '',
      '  /**',
      '   * Secret field.',
      '   */',
      '  #secret = 1;',
      '}',
      '',
    ].join('\n');
    expect(messageIds(code)).toEqual(['nonPublicJSDoc', 'nonPublicJSDoc']);
  });

  it('ignores tooling directive comments', () => {
    const code = [
      '// eslint-disable-next-line no-console -- reason',
      'console.log(1);',
      '// ts-expect-error some description',
      'const bad: string = 1;',
      '',
    ].join('\n');
    expect(messageIds(code)).toEqual([]);
  });
});
