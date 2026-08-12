import type {Linter} from 'eslint';
import {describe, expect, it} from 'vitest';
import {folderRule} from '@aimarchirico/commons-ts/folders';
import config from '../eslint-core';
import {CORE_FOLDERS} from '../folders';

describe('eslint-core', () => {
  it('is a non-empty flat config array', () => {
    expect(Array.isArray(config)).toBe(true);
    expect(config.length).toBeGreaterThan(0);
  });

  it('appends the folder naming rule for CORE_FOLDERS', () => {
    const folderBlock = config.find(
      block => block.rules?.['check-file/folder-naming-convention'],
    );
    expect(folderBlock).toEqual(folderRule(CORE_FOLDERS));
  });

  it('appends the web/android filename override', () => {
    const block = config.find(b =>
      (b.files as string[] | undefined)?.includes('**/*.{web,android}.ts'),
    );
    expect(block?.rules?.['check-file/filename-naming-convention']).toBe('off');
  });

  it('bans StyleSheet.create via no-restricted-properties', () => {
    const block = config.find(
      b =>
        Array.isArray(b.rules?.['no-restricted-properties']) &&
        (b.rules['no-restricted-properties'] as unknown[]).some(
          entry =>
            typeof entry === 'object' &&
            entry !== null &&
            (entry as {object?: string}).object === 'StyleSheet',
        ),
    );
    expect(block?.rules?.['no-restricted-properties']).toEqual([
      'error',
      {
        object: 'StyleSheet',
        property: 'create',
        message:
          'StyleSheet.create is banned. Use nativewind className instead.',
      },
    ]);
  });

  it('dedups the @typescript-eslint plugin instance across merged configs', () => {
    const withTsPlugin = config.filter(
      (
        block,
      ): block is Linter.Config & {
        plugins: NonNullable<Linter.Config['plugins']>;
      } => Boolean(block.plugins?.['@typescript-eslint']),
    );
    const instances = new Set(
      withTsPlugin.map(block => block.plugins['@typescript-eslint']),
    );
    expect(instances.size).toBeLessThanOrEqual(1);
  });

  it('dedups the import plugin instance across merged configs', () => {
    const withImportPlugin = config.filter(
      (
        block,
      ): block is Linter.Config & {
        plugins: NonNullable<Linter.Config['plugins']>;
      } => Boolean(block.plugins?.['import']),
    );
    const instances = new Set(
      withImportPlugin.map(block => block.plugins['import']),
    );
    expect(instances.size).toBeLessThanOrEqual(1);
  });
});
