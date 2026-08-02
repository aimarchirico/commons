import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {decodeGoogleServices} from '../decode-google-services.js';

const {mkdirSync, writeFileSync, log, exit} = vi.hoisted(() => ({
  mkdirSync: vi.fn(),
  writeFileSync: vi.fn(),
  log: vi.fn(),
  exit: vi.fn((code?: number) => {
    throw new Error(`process.exit(${code})`);
  }),
}));

vi.mock('fs', () => ({
  default: {mkdirSync, writeFileSync},
  mkdirSync,
  writeFileSync,
}));

describe('decode-google-services.ts', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = {...originalEnv};
    delete process.env.GOOGLE_SERVICES_JSON_BASE64;
    delete process.env.GOOGLE_SERVICES_OUTPUT_PATH;
    mkdirSync.mockReset();
    writeFileSync.mockReset();
    log.mockReset();
    exit.mockReset();
    vi.spyOn(console, 'log').mockImplementation(log);
    vi.spyOn(process, 'exit').mockImplementation(
      exit as unknown as typeof process.exit,
    );
  });

  afterEach(() => {
    process.env = originalEnv;
    vi.restoreAllMocks();
  });

  it('exits without writing when the base64 env var is unset', () => {
    expect(() => decodeGoogleServices()).toThrow('process.exit(0)');
    expect(log).toHaveBeenCalledWith(
      'GOOGLE_SERVICES_JSON_BASE64 not set, skipping google-services.json.',
    );
    expect(writeFileSync).not.toHaveBeenCalled();
  });

  it('decodes and writes to the default output path', () => {
    process.env.GOOGLE_SERVICES_JSON_BASE64 =
      Buffer.from('{"a":1}').toString('base64');

    decodeGoogleServices();

    expect(mkdirSync).toHaveBeenCalledWith('src/assets', {recursive: true});
    expect(writeFileSync).toHaveBeenCalledWith(
      'src/assets/google-services.json',
      '{"a":1}',
    );
    expect(log).toHaveBeenCalledWith('Wrote src/assets/google-services.json');
  });

  it('writes to a custom output path when set', () => {
    process.env.GOOGLE_SERVICES_JSON_BASE64 =
      Buffer.from('{"b":2}').toString('base64');
    process.env.GOOGLE_SERVICES_OUTPUT_PATH = 'custom/path.json';

    decodeGoogleServices();

    expect(mkdirSync).toHaveBeenCalledWith('custom', {recursive: true});
    expect(writeFileSync).toHaveBeenCalledWith('custom/path.json', '{"b":2}');
    expect(log).toHaveBeenCalledWith('Wrote custom/path.json');
  });
});
