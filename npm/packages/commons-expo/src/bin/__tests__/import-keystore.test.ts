import {
  fail,
  instruct,
  printSummary,
  report,
  resolveEnv,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {importKeystore} from '../import-keystore.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  instruct: vi.fn(),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
  writeOutputs: vi.fn(),
}));

const {existsSync, readFileSync, rmSync, readdirSync, rmdirSync, log} =
  vi.hoisted(() => ({
    existsSync: vi.fn(),
    readFileSync: vi.fn(),
    rmSync: vi.fn(),
    readdirSync: vi.fn(),
    rmdirSync: vi.fn(),
    log: vi.fn(),
  }));

vi.mock('fs', () => ({
  default: {existsSync, readFileSync, rmSync, readdirSync, rmdirSync},
  existsSync,
  readFileSync,
  rmSync,
  readdirSync,
  rmdirSync,
}));

describe('import-keystore.ts', () => {
  beforeEach(() => {
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(instruct).mockClear();
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveEnv).mockClear();
    vi.mocked(writeOutputs).mockClear();
    existsSync.mockReset();
    readFileSync.mockReset();
    rmSync.mockReset();
    readdirSync.mockReset();
    rmdirSync.mockReset();
    log.mockReset();
    vi.spyOn(console, 'log').mockImplementation(log);
  });

  it('reports present when ANDROID_KEYSTORE_BASE64 is already set', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ANDROID_KEYSTORE_BASE64: 'already-set',
    });

    importKeystore();

    expect(report).toHaveBeenCalledWith(
      'android signing key',
      'present',
      'ANDROID_KEYSTORE_BASE64 already set',
    );
    expect(printSummary).toHaveBeenCalledWith('import-keystore');
    expect(existsSync).not.toHaveBeenCalled();
  });

  it('instructs when credentials.json is missing', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockReturnValue(false);

    importKeystore();

    expect(instruct).toHaveBeenCalledWith(
      'android signing key',
      'no credentials.json found',
      expect.any(Array),
    );
    expect(printSummary).toHaveBeenCalledWith('import-keystore');
  });

  it('fails when credentials.json has no android.keystore entry', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockReturnValue(true);
    readFileSync.mockReturnValue(JSON.stringify({}));

    expect(() => importKeystore()).toThrow(/has no "android.keystore" entry/);
  });

  it('fails when the keystore file does not exist', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockImplementation(
      (path: string) => path === 'credentials.json',
    );
    readFileSync.mockReturnValue(
      JSON.stringify({
        android: {keystore: {keystorePath: 'missing.keystore'}},
      }),
    );

    expect(() => importKeystore()).toThrow(/which does not exist/);
  });

  it('fails when password or alias is missing', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockReturnValue(true);
    readFileSync.mockReturnValue(
      JSON.stringify({
        android: {keystore: {keystorePath: 'release.keystore'}},
      }),
    );

    expect(() => importKeystore()).toThrow(
      /missing the keystore password or key alias/,
    );
  });

  it('imports the keystore and removes local files', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockReturnValue(true);
    readdirSync.mockReturnValue([]);
    readFileSync
      .mockReturnValueOnce(
        JSON.stringify({
          android: {
            keystore: {
              keystorePath: 'android/app/release.keystore',
              keystorePassword: 'pw',
              keyAlias: 'alias',
              keyPassword: 'keypw',
            },
          },
        }),
      )
      .mockReturnValueOnce(Buffer.from('binary-keystore'));

    importKeystore();

    expect(writeOutputs).toHaveBeenCalledWith({
      ANDROID_KEYSTORE_BASE64:
        Buffer.from('binary-keystore').toString('base64'),
      ANDROID_KEYSTORE_PASSWORD: 'pw',
      ANDROID_KEY_ALIAS: 'alias',
      ANDROID_KEY_PASSWORD: 'keypw',
    });
    expect(report).toHaveBeenCalledWith(
      'android signing key',
      'written',
      'imported from credentials.json',
    );
    expect(rmSync).toHaveBeenCalledWith('android/app/release.keystore', {
      force: true,
    });
    expect(rmSync).toHaveBeenCalledWith('credentials.json', {force: true});
    expect(rmdirSync).toHaveBeenCalledWith('android/app');
    expect(printSummary).toHaveBeenCalledWith('import-keystore');
  });

  it('falls back to keystorePassword when keyPassword is absent', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockReturnValue(true);
    readdirSync.mockReturnValue(['other-file']);
    readFileSync
      .mockReturnValueOnce(
        JSON.stringify({
          android: {
            keystore: {
              keystorePath: 'android/app/release.keystore',
              keystorePassword: 'pw',
              keyAlias: 'alias',
            },
          },
        }),
      )
      .mockReturnValueOnce(Buffer.from('binary-keystore'));

    importKeystore();

    expect(writeOutputs).toHaveBeenCalledWith(
      expect.objectContaining({ANDROID_KEY_PASSWORD: 'pw'}),
    );
    expect(rmdirSync).not.toHaveBeenCalled();
  });

  it('catches non-Error exceptions and calls fail', () => {
    vi.mocked(resolveEnv).mockReturnValue({});
    existsSync.mockReturnValue(true);
    readFileSync.mockImplementation(() => {
      throw 'boom';
    });

    expect(() => importKeystore()).toThrow('fail: boom');
    expect(fail).toHaveBeenCalledWith('boom');
  });
});
