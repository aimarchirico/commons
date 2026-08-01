import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {api, resolveAccount} from './api-client';

vi.mock('@aimarchirico/commons-project', () => ({
  context: vi.fn(),
  fail: vi.fn((message: string) => {
    throw new Error(message);
  }),
}));

const jsonResponse = (status: number, payload: unknown): Response =>
  ({
    status,
    text: () => Promise.resolve(JSON.stringify(payload)),
  }) as Response;

describe('api', () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    fetchMock.mockReset();
    vi.unstubAllGlobals();
  });

  it('get returns the result on success', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(200, {success: true, result: {id: '1'}}),
    );
    const client = api('token');
    await expect(client.get('/accounts')).resolves.toEqual({id: '1'});
  });

  it('get returns undefined for a 404', async () => {
    fetchMock.mockResolvedValue(jsonResponse(404, {success: false}));
    const client = api('token');
    await expect(client.get('/missing')).resolves.toBeUndefined();
  });

  it('get throws with the Cloudflare error detail on failure', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(400, {
        success: false,
        errors: [{code: 1, message: 'bad request'}],
      }),
    );
    const client = api('token');
    await expect(client.get('/broken')).rejects.toThrow(
      '/broken failed: 1 bad request',
    );
  });

  it('get throws with an unresponsive message when no errors are given', async () => {
    fetchMock.mockResolvedValue(jsonResponse(400, {success: false}));
    const client = api('token');
    await expect(client.get('/broken')).rejects.toThrow(
      'unknown Cloudflare error',
    );
  });

  it('throws when the response body is not JSON', async () => {
    fetchMock.mockResolvedValue({
      status: 500,
      text: () => Promise.resolve('<html>oops</html>'),
    } as Response);
    const client = api('token');
    await expect(client.get('/broken')).rejects.toThrow(
      'GET /broken returned 500',
    );
  });

  it('send returns the result on success', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(200, {success: true, result: {ok: true}}),
    );
    const client = api('token');
    await expect(client.send('POST', '/things', {a: 1})).resolves.toEqual({
      ok: true,
    });
  });

  it('send throws on failure', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(400, {
        success: false,
        errors: [{code: 2, message: 'nope'}],
      }),
    );
    const client = api('token');
    await expect(client.send('DELETE', '/things')).rejects.toThrow(
      '/things failed: 2 nope',
    );
  });
});

describe('resolveAccount', () => {
  it('uses the override when provided', async () => {
    const client = {get: vi.fn(), send: vi.fn()};
    await expect(resolveAccount(client, 'account-1')).resolves.toBe(
      'account-1',
    );
    expect(client.get).not.toHaveBeenCalled();
  });

  it('resolves the single account the token can see', async () => {
    const client = {
      get: vi.fn().mockResolvedValue([{id: 'acc-1', name: 'Only Account'}]),
      send: vi.fn(),
    };
    await expect(resolveAccount(client)).resolves.toBe('acc-1');
  });

  it('fails when the token sees no accounts', async () => {
    const client = {get: vi.fn().mockResolvedValue([]), send: vi.fn()};
    await expect(resolveAccount(client)).rejects.toThrow(
      'can see no accounts',
    );
  });

  it('fails when the token sees more than one account', async () => {
    const client = {
      get: vi.fn().mockResolvedValue([
        {id: 'acc-1', name: 'One'},
        {id: 'acc-2', name: 'Two'},
      ]),
      send: vi.fn(),
    };
    await expect(resolveAccount(client)).rejects.toThrow('can see 2 accounts');
  });
});
