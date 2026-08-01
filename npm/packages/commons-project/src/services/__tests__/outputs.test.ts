import fs from 'fs';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {writeOutputs} from '../outputs';

describe('writeOutputs', () => {
  let logSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
    delete process.env.OUTPUT_FILE;
  });

  it('does nothing when there are no values', () => {
    const appendSpy = vi
      .spyOn(fs, 'appendFileSync')
      .mockImplementation(() => {});
    writeOutputs({});
    expect(appendSpy).not.toHaveBeenCalled();
    expect(logSpy).not.toHaveBeenCalled();
  });

  it('prints masked secrets when OUTPUT_FILE is unset', () => {
    delete process.env.OUTPUT_FILE;
    writeOutputs({API_TOKEN: 'sekrit', NAME: 'hello'});
    expect(logSpy).toHaveBeenCalledWith('  API_TOKEN=<6 characters>');
    expect(logSpy).toHaveBeenCalledWith('  NAME=hello');
  });

  it('appends KEY=value lines when OUTPUT_FILE is set', () => {
    process.env.OUTPUT_FILE = '/tmp/out.env';
    const appendSpy = vi
      .spyOn(fs, 'appendFileSync')
      .mockImplementation(() => {});
    writeOutputs({A: '1', B: '2'});
    expect(appendSpy).toHaveBeenCalledWith('/tmp/out.env', 'A=1\nB=2\n', {
      mode: 0o600,
    });
    expect(logSpy).toHaveBeenCalledWith(
      '  outputs written to /tmp/out.env: A, B',
    );
  });
});
