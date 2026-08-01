import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {collectEnv, resolveEnv, resolveEnvList} from './env';

const KEYS = ['TEST_REQUIRED_A', 'TEST_REQUIRED_B', 'TEST_OPTIONAL'];

describe('resolveEnv', () => {
  afterEach(() => {
    for (const key of KEYS) delete process.env[key];
    vi.restoreAllMocks();
  });

  it('resolves required and optional variables', () => {
    process.env.TEST_REQUIRED_A = 'a';
    process.env.TEST_REQUIRED_B = 'b';
    process.env.TEST_OPTIONAL = 'opt';
    expect(
      resolveEnv(['TEST_REQUIRED_A', 'TEST_REQUIRED_B'], ['TEST_OPTIONAL']),
    ).toEqual({
      TEST_REQUIRED_A: 'a',
      TEST_REQUIRED_B: 'b',
      TEST_OPTIONAL: 'opt',
    });
  });

  it('resolves an unset optional variable to undefined', () => {
    process.env.TEST_REQUIRED_A = 'a';
    expect(resolveEnv(['TEST_REQUIRED_A'], ['TEST_OPTIONAL'])).toEqual({
      TEST_REQUIRED_A: 'a',
      TEST_OPTIONAL: undefined,
    });
  });

  it('treats a blank required variable as missing and exits reporting every gap', () => {
    process.env.TEST_REQUIRED_A = '   ';
    const exitSpy = vi
      .spyOn(process, 'exit')
      .mockImplementation(() => undefined as never);
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    resolveEnv(['TEST_REQUIRED_A', 'TEST_REQUIRED_B']);

    expect(exitSpy).toHaveBeenCalledWith(1);
    const message = errorSpy.mock.calls.map(call => call.join(' ')).join('\n');
    expect(message).toContain('TEST_REQUIRED_A');
    expect(message).toContain('TEST_REQUIRED_B');
  });
});

describe('collectEnv', () => {
  afterEach(() => {
    for (const key of KEYS) delete process.env[key];
  });

  it('collects only the variables that are set', () => {
    process.env.TEST_REQUIRED_A = 'a';
    expect(collectEnv(['TEST_REQUIRED_A', 'TEST_REQUIRED_B'])).toEqual({
      TEST_REQUIRED_A: 'a',
    });
  });
});

describe('resolveEnvList', () => {
  beforeEach(() => {
    process.env.TEST_REQUIRED_A = 'a';
    process.env.TEST_REQUIRED_B = 'b';
  });

  afterEach(() => {
    for (const key of KEYS) delete process.env[key];
  });

  it('reads the variables named by a comma/space separated list', () => {
    expect(resolveEnvList('TEST_REQUIRED_A, TEST_REQUIRED_B')).toEqual({
      TEST_REQUIRED_A: 'a',
      TEST_REQUIRED_B: 'b',
    });
  });
});
