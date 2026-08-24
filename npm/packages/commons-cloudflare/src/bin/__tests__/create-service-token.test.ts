import {
  fail,
  printSummary,
  report,
  resolveEnv,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {createServiceToken} from '../create-service-token.js';
import {api, resolveAccount} from '../../services/api-client.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
  writeOutputs: vi.fn(),
}));

const {get, send} = vi.hoisted(() => ({
  get: vi.fn(),
  send: vi.fn(),
}));

vi.mock('../../services/api-client.js', () => ({
  api: vi.fn(() => ({get, send})),
  resolveAccount: vi.fn(),
}));

describe('create-service-token.ts', () => {
  beforeEach(() => {
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveEnv).mockClear();
    vi.mocked(writeOutputs).mockClear();
    vi.mocked(api).mockClear();
    vi.mocked(resolveAccount).mockClear();
    get.mockReset();
    send.mockReset();

    vi.mocked(resolveEnv).mockReturnValue({
      CLOUDFLARE_API_TOKEN: 'token',
      SERVICE_TOKEN_NAME: 'my-token',
      ACCESS_POLICY_ID: 'policy-1',
    });
    vi.mocked(resolveAccount).mockResolvedValue('account-1');
  });

  it('creates a new token and attaches it to the policy', async () => {
    get.mockResolvedValueOnce([]).mockResolvedValueOnce({include: []});
    send.mockResolvedValueOnce({
      id: 'tok-1',
      name: 'my-token',
      client_id: 'client-1',
      client_secret: 'secret-1',
    });

    await createServiceToken();

    expect(report).toHaveBeenCalledWith('service token my-token', 'created');
    expect(writeOutputs).toHaveBeenCalledWith({
      CF_ACCESS_CLIENT_ID: 'client-1',
      CF_ACCESS_CLIENT_SECRET: 'secret-1',
    });
    expect(send).toHaveBeenCalledWith(
      'PUT',
      '/accounts/account-1/access/policies/policy-1',
      {
        include: [{service_token: {token_id: 'tok-1'}}],
      },
    );
    expect(report).toHaveBeenCalledWith(
      'policy policy-1',
      'updated',
      'includes my-token',
    );
    expect(printSummary).toHaveBeenCalledWith(
      'commons-cloudflare create-service-token',
    );
  });

  it('reuses an existing token and reports it cannot be re-read', async () => {
    get
      .mockResolvedValueOnce([
        {id: 'tok-1', name: 'my-token', client_id: 'client-1'},
      ])
      .mockResolvedValueOnce({
        include: [{service_token: {token_id: 'tok-1'}}],
      });

    await createServiceToken();

    expect(report).toHaveBeenCalledWith(
      'service token my-token',
      'present',
      'secret cannot be re-read; reuse the stored value or rotate deliberately',
    );
    expect(writeOutputs).toHaveBeenCalledWith({
      CF_ACCESS_CLIENT_ID: 'client-1',
    });
    expect(report).toHaveBeenCalledWith(
      'policy policy-1',
      'present',
      'includes my-token',
    );
    expect(send).not.toHaveBeenCalled();
  });

  it('fails when the Access policy is missing', async () => {
    get.mockResolvedValueOnce([]).mockResolvedValueOnce(undefined);
    send.mockResolvedValueOnce({
      id: 'tok-1',
      name: 'my-token',
      client_id: 'client-1',
    });

    await expect(createServiceToken()).rejects.toThrow(
      'No Access policy policy-1 in account account-1.',
    );
  });

  it('catches non-Error exceptions and calls fail', async () => {
    get.mockRejectedValue('boom');

    await expect(createServiceToken()).rejects.toThrow('fail: boom');
    expect(fail).toHaveBeenCalledWith('boom');
  });
});
