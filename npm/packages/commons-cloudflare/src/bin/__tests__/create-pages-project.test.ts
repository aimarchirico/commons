import {
  context,
  defaultBranch,
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {createPagesProject} from '../create-pages-project.js';
import {api, resolveAccount} from '../../services/api-client.js';

vi.mock('@aimarchirico/commons-project', () => ({
  context: vi.fn(),
  defaultBranch: vi.fn(),
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

describe('create-pages-project.ts', () => {
  beforeEach(() => {
    vi.mocked(context).mockClear();
    vi.mocked(defaultBranch).mockClear();
    vi.mocked(defaultBranch).mockReturnValue('main');
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
      PAGES_CUSTOM_DOMAIN: 'example.com',
    });
    vi.mocked(resolveAccount).mockResolvedValue('account-1');
  });

  it('creates project and domain when neither exists', async () => {
    get.mockResolvedValueOnce(undefined).mockResolvedValueOnce([]);

    await createPagesProject();

    expect(send).toHaveBeenCalledWith(
      'POST',
      '/accounts/account-1/pages/projects',
      {name: 'my-project', production_branch: 'main'},
    );
    expect(report).toHaveBeenCalledWith('pages project my-project', 'created');
    expect(send).toHaveBeenCalledWith(
      'POST',
      '/accounts/account-1/pages/projects/my-project/domains',
      {name: 'example.com'},
    );
    expect(send).toHaveBeenCalledWith(
      'PATCH',
      '/accounts/account-1/pages/projects/my-project/domains/example.com',
      {},
    );
    expect(report).toHaveBeenCalledWith(
      'custom domain example.com',
      'created',
      'automatic DNS requested',
    );
    expect(printSummary).toHaveBeenCalledWith('create-pages-project');
  });

  it('falls back to main when there is no derived default branch', async () => {
    vi.mocked(defaultBranch).mockReturnValue(undefined);
    get.mockResolvedValueOnce(undefined).mockResolvedValueOnce([]);

    await createPagesProject();

    expect(context).toHaveBeenCalledWith(
      'production branch',
      'main',
      'no remote, assumed default',
    );
  });

  it('reports present when project and domain already exist', async () => {
    get
      .mockResolvedValueOnce({name: 'my-project'})
      .mockResolvedValueOnce([{name: 'example.com'}]);

    await createPagesProject();

    expect(report).toHaveBeenCalledWith('pages project my-project', 'present');
    expect(report).toHaveBeenCalledWith('custom domain example.com', 'present');
    expect(send).not.toHaveBeenCalled();
  });

  it('catches non-Error exceptions and calls fail', async () => {
    get.mockRejectedValue('boom');

    await expect(createPagesProject()).rejects.toThrow('fail: boom');
    expect(fail).toHaveBeenCalledWith('boom');
  });
});
