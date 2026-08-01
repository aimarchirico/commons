import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
  type MockInstance,
} from 'vitest';

const freshReportModule = async () => {
  vi.resetModules();
  return import('../report');
};

describe('report service', () => {
  let logSpy: MockInstance<typeof console.log>;
  let errorSpy: MockInstance<typeof console.error>;
  let exitSpy: MockInstance<typeof process.exit>;

  beforeEach(() => {
    logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    exitSpy = vi
      .spyOn(process, 'exit')
      .mockImplementation(() => undefined as never);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('report prints the mark, resource, and label', async () => {
    const {report} = await freshReportModule();
    report('widget', 'created');
    expect(logSpy).toHaveBeenCalledWith('+ widget: created');
  });

  it('report appends the detail when given', async () => {
    const {report} = await freshReportModule();
    report('widget', 'updated', 'renamed');
    expect(logSpy).toHaveBeenCalledWith('~ widget: updated (renamed)');
  });

  it('context prints the derivation', async () => {
    const {context} = await freshReportModule();
    context('account', '123', 'from token');
    expect(logSpy).toHaveBeenCalledWith('· account 123 (from token)');
  });

  it('instruct reports pending and records the instruction', async () => {
    const {instruct, printSummary} = await freshReportModule();
    instruct('keystore', 'not provisioned', ['step one', 'step two']);
    expect(logSpy).toHaveBeenCalledWith(
      '! keystore: action required (not provisioned)',
    );
    printSummary('Summary');
    const output = logSpy.mock.calls.map(call => call.join(' ')).join('\n');
    expect(output).toContain('Action required — keystore:');
    expect(output).toContain('step one');
    expect(output).toContain('step two');
  });

  it('step reports the outcome and returns the value', async () => {
    const {step} = await freshReportModule();
    const value = await step('token', async () => ({
      outcome: 'created' as const,
      value: 'abc',
    }));
    expect(value).toBe('abc');
    expect(logSpy).toHaveBeenCalledWith('+ token: created');
  });

  it('step reports a failure and exits', async () => {
    const {step} = await freshReportModule();
    await step('token', async () => {
      throw new Error('boom');
    });
    expect(errorSpy).toHaveBeenCalledWith('! token: failed\n  boom');
    expect(exitSpy).toHaveBeenCalledWith(1);
  });

  it('printSummary reports "nothing to do" with no entries', async () => {
    const {printSummary} = await freshReportModule();
    printSummary('Nothing');
    expect(logSpy).toHaveBeenCalledWith(
      expect.stringContaining('nothing to do'),
    );
  });

  it('printSummary reports a settled run with no changes', async () => {
    const {report, printSummary} = await freshReportModule();
    report('widget', 'present');
    printSummary('Settled');
    const output = logSpy.mock.calls.map(call => call.join(' ')).join('\n');
    expect(output).toContain('no changes');
  });

  it('fail logs the message and exits', async () => {
    const {fail} = await freshReportModule();
    expect(() => fail('nope')).not.toThrow();
    expect(errorSpy).toHaveBeenCalledWith('nope');
    expect(exitSpy).toHaveBeenCalledWith(1);
  });
});
