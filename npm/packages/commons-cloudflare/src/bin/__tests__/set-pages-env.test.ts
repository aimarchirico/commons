import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {setPagesEnv} from '../set-pages-env.js';
import {api, resolveAccount} from '../../services/api-client.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
}));

const {get, send} = vi.hoisted(() => ({
  get: vi.fn(),
  send: vi.fn(),
}));

vi.mock('../../services/api-client.js', () => ({
  api: vi.fn(() => ({get, send})),
  resolveAccount: vi.fn(),
}));

describe('set-pages-env.ts', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = {...originalEnv};
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveEnv).mockClear();
    vi.mocked(api).mockClear();
    vi.mocked(resolveAccount).mockClear();
    get.mockReset();
    send.mockReset();

    vi.mocked(resolveEnv).mockReturnValue({
      CLOUDFLARE_API_TOKEN: 'token',
      PAGES_PROJECT_NAME: 'my-project',
      PAGES_VARIABLES: 'FOO,BAR',
    });
    vi.mocked(resolveAccount).mockResolvedValue('account-1');
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('fails when the Pages project does not exist', async () => {
    get.mockResolvedValue(undefined);

    await expect(setPagesEnv()).rejects.toThrow(
      'No Pages project "my-project". Run create-pages-project first.',
    );
  });

  it('skips variables not set in the environment', async () => {
    delete process.env.FOO;
    delete process.env.BAR;
    get.mockResolvedValue({deployment_configs: {}});

    await setPagesEnv();

    expect(report).toHaveBeenCalledWith(
      'pages production FOO',
      'skipped',
      'not set in the environment',
    );
    expect(send).not.toHaveBeenCalled();
  });

  it('reports present when the value already matches', async () => {
    process.env.FOO = 'value';
    process.env.BAR = '';
    get.mockResolvedValue({
      deployment_configs: {
        production: {env_vars: {FOO: {type: 'plain_text', value: 'value'}}},
      },
    });

    await setPagesEnv();

    expect(report).toHaveBeenCalledWith(
      'pages production FOO',
      'present',
      'value already correct',
    );
    expect(send).not.toHaveBeenCalled();
  });

  it('creates and updates changed variables', async () => {
    process.env.FOO = 'new-foo';
    process.env.BAR = 'new-bar';
    get.mockResolvedValue({
      deployment_configs: {
        production: {env_vars: {FOO: {type: 'plain_text', value: 'old-foo'}}},
      },
    });

    await setPagesEnv();

    expect(report).toHaveBeenCalledWith('pages production FOO', 'updated');
    expect(report).toHaveBeenCalledWith('pages production BAR', 'created');
    expect(send).toHaveBeenCalledWith(
      'PATCH',
      '/accounts/account-1/pages/projects/my-project',
      {
        deployment_configs: {
          production: {
            env_vars: {
              FOO: {type: 'plain_text', value: 'new-foo'},
              BAR: {type: 'plain_text', value: 'new-bar'},
            },
          },
        },
      },
    );
    expect(printSummary).toHaveBeenCalledWith(
      'commons-cloudflare set-pages-env',
    );
  });

  it('catches non-Error exceptions and calls fail', async () => {
    get.mockRejectedValue('boom');

    await expect(setPagesEnv()).rejects.toThrow('fail: boom');
    expect(fail).toHaveBeenCalledWith('boom');
  });

  it('writes secrets as secret_text and skips unset ones', async () => {
    vi.mocked(resolveEnv).mockReturnValue({
      CLOUDFLARE_API_TOKEN: 'token',
      PAGES_PROJECT_NAME: 'my-project',
      PAGES_VARIABLES: '',
      PAGES_SECRETS: 'SECRET_ONE,SECRET_TWO',
    });
    process.env.SECRET_ONE = 'secret-value';
    delete process.env.SECRET_TWO;
    get.mockResolvedValue({
      deployment_configs: {
        production: {
          env_vars: {SECRET_ONE: {type: 'secret_text', value: null}},
        },
      },
    });

    await setPagesEnv();

    expect(report).toHaveBeenCalledWith(
      'pages production SECRET_TWO',
      'skipped',
      'not set in the environment',
    );
    expect(report).toHaveBeenCalledWith(
      'pages production SECRET_ONE',
      'updated',
      'secret value cannot be diffed, written unconditionally',
    );
    expect(send).toHaveBeenCalledWith(
      'PATCH',
      '/accounts/account-1/pages/projects/my-project',
      {
        deployment_configs: {
          production: {
            env_vars: {
              SECRET_ONE: {type: 'secret_text', value: 'secret-value'},
            },
          },
        },
      },
    );
  });

  it('reports a new secret as created when none exists yet', async () => {
    vi.mocked(resolveEnv).mockReturnValue({
      CLOUDFLARE_API_TOKEN: 'token',
      PAGES_PROJECT_NAME: 'my-project',
      PAGES_VARIABLES: '',
      PAGES_SECRETS: 'PROXY_SECRET',
    });
    process.env.PROXY_SECRET = 'shared-secret';
    get.mockResolvedValue({deployment_configs: {}});

    await setPagesEnv();

    expect(report).toHaveBeenCalledWith(
      'pages production PROXY_SECRET',
      'created',
      'secret value cannot be diffed, written unconditionally',
    );
  });
});
