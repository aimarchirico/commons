import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {buildAndroid} from '../build-android.js';

const {existsSync, writeFileSync, spawnSync, log, error, exit} = vi.hoisted(
  () => ({
    existsSync: vi.fn(),
    writeFileSync: vi.fn(),
    spawnSync: vi.fn(),
    log: vi.fn(),
    error: vi.fn(),
    exit: vi.fn((code?: number) => {
      throw new Error(`process.exit(${code})`);
    }),
  }),
);

vi.mock('fs', () => ({
  default: {existsSync, writeFileSync},
  existsSync,
  writeFileSync,
}));

vi.mock('child_process', () => ({spawnSync}));

describe('build-android.ts', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = {...originalEnv};
    delete process.env.ANDROID_KEYSTORE_BASE64;
    delete process.env.ANDROID_KEYSTORE_PASSWORD;
    delete process.env.ANDROID_KEY_ALIAS;
    delete process.env.ANDROID_KEY_PASSWORD;
    delete process.env.ANDROID_ALLOW_UNSIGNED;
    existsSync.mockReset();
    writeFileSync.mockReset();
    spawnSync.mockReset();
    log.mockReset();
    error.mockReset();
    exit.mockReset();
    vi.spyOn(console, 'log').mockImplementation(log);
    vi.spyOn(console, 'error').mockImplementation(error);
    vi.spyOn(process, 'exit').mockImplementation(
      exit as unknown as typeof process.exit,
    );
  });

  afterEach(() => {
    process.env = originalEnv;
    vi.restoreAllMocks();
  });

  it('exits when the android directory does not exist', () => {
    existsSync.mockReturnValue(false);

    expect(() => buildAndroid()).toThrow('process.exit(1)');
    expect(error).toHaveBeenCalledWith(
      'No android/ directory found. Run "expo prebuild" first.',
    );
  });

  it('exits when keystore is not set and unsigned builds are not allowed', () => {
    existsSync.mockReturnValue(true);

    expect(() => buildAndroid()).toThrow('process.exit(1)');
    expect(spawnSync).not.toHaveBeenCalled();
  });

  it('builds unsigned when ANDROID_ALLOW_UNSIGNED is set', () => {
    existsSync.mockReturnValue(true);
    process.env.ANDROID_ALLOW_UNSIGNED = '1';
    spawnSync.mockReturnValue({status: 0, error: undefined});

    expect(() => buildAndroid()).toThrow('process.exit(0)');
    expect(log).toHaveBeenCalledWith(
      'ANDROID_KEYSTORE_BASE64 not set, building with default (debug) signing.',
    );
    expect(spawnSync).toHaveBeenCalledWith(
      'bash',
      ['gradlew', 'assembleRelease'],
      expect.objectContaining({stdio: 'inherit'}),
    );
  });

  it('exits when keystore is set but companion variables are missing', () => {
    existsSync.mockReturnValue(true);
    process.env.ANDROID_KEYSTORE_BASE64 = 'base64data';

    expect(() => buildAndroid()).toThrow('process.exit(1)');
    expect(error).toHaveBeenCalledWith(
      expect.stringContaining('ANDROID_KEYSTORE_BASE64 is set but missing'),
    );
  });

  it('writes the keystore and builds signed when all variables are set', () => {
    existsSync.mockReturnValue(true);
    process.env.ANDROID_KEYSTORE_BASE64 = Buffer.from('key').toString('base64');
    process.env.ANDROID_KEYSTORE_PASSWORD = 'pw';
    process.env.ANDROID_KEY_ALIAS = 'alias';
    process.env.ANDROID_KEY_PASSWORD = 'keypw';
    spawnSync.mockReturnValue({status: 0, error: undefined});

    expect(() => buildAndroid()).toThrow('process.exit(0)');
    expect(writeFileSync).toHaveBeenCalled();
    expect(spawnSync).toHaveBeenCalledWith(
      'bash',
      expect.arrayContaining([
        'gradlew',
        'assembleRelease',
        expect.stringContaining('signing.store.password=pw'),
      ]),
      expect.any(Object),
    );
  });

  it('exits with error when spawnSync reports an error', () => {
    existsSync.mockReturnValue(true);
    process.env.ANDROID_ALLOW_UNSIGNED = '1';
    spawnSync.mockReturnValue({error: new Error('spawn failed')});

    expect(() => buildAndroid()).toThrow('process.exit(1)');
    expect(error).toHaveBeenCalledWith('spawn failed');
  });

  it('exits with 1 when spawnSync returns no status', () => {
    existsSync.mockReturnValue(true);
    process.env.ANDROID_ALLOW_UNSIGNED = '1';
    spawnSync.mockReturnValue({status: null, error: undefined});

    expect(() => buildAndroid()).toThrow('process.exit(1)');
  });
});
