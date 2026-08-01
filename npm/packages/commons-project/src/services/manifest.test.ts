import fs from 'fs';
import path from 'path';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {interpolate, loadManifest, manifestPath} from './manifest';
import type {ManifestValue} from '../types/manifest';

const values: Record<string, ManifestValue> = {
  name: {from: 'Template', to: 'My App'},
};

describe('interpolate', () => {
  it('resolves an unqualified placeholder using the given side', () => {
    expect(interpolate('{{name}}', 'from', values)).toBe('Template');
    expect(interpolate('{{name}}', 'to', values)).toBe('My App');
  });

  it('resolves an explicit side regardless of the given side', () => {
    expect(interpolate('{{name.to}}', 'from', values)).toBe('My App');
  });

  it('applies a transform', () => {
    expect(interpolate('{{name|kebab}}', 'to', values)).toBe('my-app');
  });

  it('applies a transform to an explicit side', () => {
    expect(interpolate('{{name.from|kebab}}', 'to', values)).toBe('template');
  });

  it('throws for an unknown manifest value', () => {
    expect(() => interpolate('{{missing}}', 'from', values)).toThrow(
      'Unknown manifest value "missing"',
    );
  });
});

describe('manifestPath', () => {
  const original = process.env.MANIFEST_PATH;

  afterEach(() => {
    if (original === undefined) delete process.env.MANIFEST_PATH;
    else process.env.MANIFEST_PATH = original;
  });

  it('defaults to manifest.json in the working directory', () => {
    delete process.env.MANIFEST_PATH;
    expect(manifestPath()).toBe(path.resolve('manifest.json'));
  });

  it('honors MANIFEST_PATH', () => {
    process.env.MANIFEST_PATH = 'custom/manifest.json';
    expect(manifestPath()).toBe(path.resolve('custom/manifest.json'));
  });
});

describe('loadManifest', () => {
  const original = process.env.MANIFEST_PATH;

  beforeEach(() => {
    process.env.MANIFEST_PATH = 'manifest.json';
  });

  afterEach(() => {
    vi.restoreAllMocks();
    if (original === undefined) delete process.env.MANIFEST_PATH;
    else process.env.MANIFEST_PATH = original;
  });

  it('throws when the manifest file is missing', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(false);
    expect(() => loadManifest()).toThrow('No manifest at');
  });

  it('throws when the manifest is not valid JSON', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue('not json');
    expect(() => loadManifest()).toThrow('is not valid JSON');
  });

  it('throws when the manifest is not an object', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue('[]');
    expect(() => loadManifest()).toThrow('Manifest must be a JSON object');
  });

  it('collects every validation error at once', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue(
      JSON.stringify({
        values: {broken: {from: '', to: 'x'}},
        replacements: [{value: 'missing', files: []}],
        moves: [{from: '{{missing}}', to: 1}],
        deletes: 'nope',
      }),
    );
    try {
      loadManifest();
      throw new Error('expected loadManifest to throw');
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      expect(message).toContain('values.broken');
      expect(message).toContain('replacements[0].value');
      expect(message).toContain('replacements[0].files');
      expect(message).toContain('moves[0]');
      expect(message).toContain('"deletes" must be an array of paths.');
    }
  });

  it('flags unknown transforms in a replacement', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue(
      JSON.stringify({
        values: {name: {from: 'a', to: 'b'}},
        replacements: [
          {value: 'name', files: ['**/*.ts'], transforms: ['nope']},
        ],
      }),
    );
    expect(() => loadManifest()).toThrow('unknown transform "nope"');
  });

  it('flags unknown placeholders and transforms in a move', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue(
      JSON.stringify({
        values: {name: {from: 'a', to: 'b'}},
        moves: [{from: '{{name|nope}}', to: '{{missing}}'}],
      }),
    );
    expect(() => loadManifest()).toThrow(/unknown transform "nope"/);
  });

  it('returns the validated manifest on success', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue(
      JSON.stringify({
        values: {name: {from: 'Template', to: 'My App'}},
        replacements: [{value: 'name', files: ['**/*.ts']}],
        moves: [{from: 'a', to: 'b'}],
        deletes: ['README.md'],
      }),
    );
    expect(loadManifest()).toEqual({
      values: {name: {from: 'Template', to: 'My App'}},
      replacements: [{value: 'name', files: ['**/*.ts']}],
      moves: [{from: 'a', to: 'b'}],
      deletes: ['README.md'],
    });
  });

  it('defaults optional sections to empty collections', () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(fs, 'readFileSync').mockReturnValue(
      JSON.stringify({values: {}}),
    );
    expect(loadManifest()).toEqual({
      values: {},
      replacements: [],
      moves: [],
      deletes: [],
    });
  });
});
