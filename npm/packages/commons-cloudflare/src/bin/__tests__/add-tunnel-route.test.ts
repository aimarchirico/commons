import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {addTunnelRoute} from '../add-tunnel-route.js';
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

describe('add-tunnel-route.ts', () => {
  beforeEach(() => {
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
      TUNNEL_ID: 'tunnel-1',
      TUNNEL_HOSTNAME: 'app.example.com',
      TUNNEL_SERVICE: 'http://localhost:8080',
    });
    vi.mocked(resolveAccount).mockResolvedValue('account-1');
  });

  it('fails when the tunnel does not exist', async () => {
    get.mockResolvedValue(undefined);

    await expect(addTunnelRoute()).rejects.toThrow(
      'fail: No tunnel tunnel-1 in account account-1.',
    );
  });

  it('reports present when the route already matches', async () => {
    get.mockResolvedValue({
      config: {
        ingress: [
          {hostname: 'app.example.com', service: 'http://localhost:8080'},
        ],
      },
    });

    await addTunnelRoute();

    expect(report).toHaveBeenCalledWith(
      'tunnel route app.example.com',
      'present',
      '→ http://localhost:8080',
    );
    expect(send).not.toHaveBeenCalled();
  });

  it('updates an existing route pointing elsewhere', async () => {
    get.mockResolvedValue({
      config: {
        ingress: [
          {hostname: 'app.example.com', service: 'http://localhost:9090'},
        ],
      },
    });

    await addTunnelRoute();

    expect(send).toHaveBeenCalledWith(
      'PUT',
      '/accounts/account-1/cfd_tunnel/tunnel-1/configurations',
      expect.objectContaining({
        config: expect.objectContaining({
          ingress: [
            {hostname: 'app.example.com', service: 'http://localhost:8080'},
          ],
        }),
      }),
    );
    expect(report).toHaveBeenCalledWith(
      'tunnel route app.example.com',
      'updated',
      '→ http://localhost:8080',
    );
  });

  it('creates a new route inserted before the catch-all rule', async () => {
    get.mockResolvedValue({
      config: {ingress: [{service: 'http://catch-all'}]},
    });

    await addTunnelRoute();

    expect(send).toHaveBeenCalledWith(
      'PUT',
      '/accounts/account-1/cfd_tunnel/tunnel-1/configurations',
      {
        config: {
          ingress: [
            {hostname: 'app.example.com', service: 'http://localhost:8080'},
            {service: 'http://catch-all'},
          ],
        },
      },
    );
    expect(report).toHaveBeenCalledWith(
      'tunnel route app.example.com',
      'created',
      '→ http://localhost:8080',
    );
  });

  it('appends a new route when there is no catch-all rule', async () => {
    get.mockResolvedValue({config: {ingress: []}});

    await addTunnelRoute();

    expect(send).toHaveBeenCalledWith(
      'PUT',
      '/accounts/account-1/cfd_tunnel/tunnel-1/configurations',
      {
        config: {
          ingress: [
            {hostname: 'app.example.com', service: 'http://localhost:8080'},
          ],
        },
      },
    );
  });

  it('scopes routes by path when TUNNEL_PATH is set', async () => {
    vi.mocked(resolveEnv).mockReturnValue({
      CLOUDFLARE_API_TOKEN: 'token',
      TUNNEL_ID: 'tunnel-1',
      TUNNEL_HOSTNAME: 'app.example.com',
      TUNNEL_SERVICE: 'http://localhost:8080',
      TUNNEL_PATH: 'api',
    });
    get.mockResolvedValue({config: {ingress: []}});

    await addTunnelRoute();

    expect(report).toHaveBeenCalledWith(
      'tunnel route app.example.com/api',
      'created',
      '→ http://localhost:8080',
    );
  });

  it('catches non-Error exceptions and calls fail', async () => {
    get.mockRejectedValue('boom');

    await expect(addTunnelRoute()).rejects.toThrow('fail: boom');
    expect(fail).toHaveBeenCalledWith('boom');
  });
});
