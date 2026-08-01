import path from 'path';
import {describe, expect, it} from 'vitest';
import {
  buildAccessHeaders,
  buildSpecUrl,
  resolveDocsDir,
  resolveOutputDir,
  toGeneratorSpecPath,
} from './openapi-client';

describe('buildSpecUrl', () => {
  it('appends the v3 api-docs path', () => {
    expect(buildSpecUrl('https://api.example.com')).toBe(
      'https://api.example.com/v3/api-docs',
    );
  });
});

describe('buildAccessHeaders', () => {
  it('builds the Cloudflare Access headers when both halves are present', () => {
    expect(buildAccessHeaders('id', 'secret')).toEqual({
      'CF-Access-Client-Id': 'id',
      'CF-Access-Client-Secret': 'secret',
    });
  });

  it('returns an empty object when the client id is missing', () => {
    expect(buildAccessHeaders(undefined, 'secret')).toEqual({});
  });

  it('returns an empty object when the client secret is missing', () => {
    expect(buildAccessHeaders('id', undefined)).toEqual({});
  });

  it('returns an empty object when both are missing', () => {
    expect(buildAccessHeaders(undefined, undefined)).toEqual({});
  });
});

describe('resolveOutputDir', () => {
  it('defaults to src/services/generated under the working directory', () => {
    expect(resolveOutputDir(undefined)).toBe(
      path.resolve(process.cwd(), 'src/services/generated'),
    );
  });

  it('resolves an override relative to the working directory', () => {
    expect(resolveOutputDir('custom/out')).toBe(
      path.resolve(process.cwd(), 'custom/out'),
    );
  });
});

describe('resolveDocsDir', () => {
  it('defaults to docs under the working directory', () => {
    expect(resolveDocsDir(undefined)).toBe(path.resolve(process.cwd(), 'docs'));
  });

  it('resolves an override relative to the working directory', () => {
    expect(resolveDocsDir('custom/docs')).toBe(
      path.resolve(process.cwd(), 'custom/docs'),
    );
  });
});

describe('toGeneratorSpecPath', () => {
  it('converts backslashes to forward slashes', () => {
    expect(toGeneratorSpecPath('C:\\tmp\\spec.json')).toBe('C:/tmp/spec.json');
  });

  it('leaves forward-slash paths unchanged', () => {
    expect(toGeneratorSpecPath('/tmp/spec.json')).toBe('/tmp/spec.json');
  });
});
