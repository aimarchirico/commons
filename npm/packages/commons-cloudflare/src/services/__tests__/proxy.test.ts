import {afterEach, describe, expect, it, vi} from 'vitest';
import {onRequest} from '../proxy';

describe('onRequest', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns 500 when API_URL is not configured', async () => {
    const response = await onRequest({
      env: {},
      request: new Request('https://example.com/api/things'),
    });
    expect(response.status).toBe(500);
    expect(await response.text()).toBe('API_URL not configured');
  });

  it('forwards the request to the backend and streams the response back', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response('ok', {
        status: 201,
        statusText: 'Created',
        headers: {'x-custom': 'yes'},
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const response = await onRequest({
      env: {API_URL: 'https://backend.internal', PROXY_SECRET: 'shh'},
      request: new Request('https://example.com/api/things?x=1', {
        method: 'GET',
      }),
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [backendUrl, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(backendUrl).toBe('https://backend.internal/things?x=1');
    const headers = init.headers as Headers;
    expect(headers.get('x-proxy-secret')).toBe('shh');
    expect(headers.get('x-forwarded-prefix')).toBe('/api');
    expect(headers.get('host')).toBeNull();

    expect(response.status).toBe(201);
    expect(response.statusText).toBe('Created');
    expect(await response.text()).toBe('ok');
  });

  it('omits the proxy secret header when unset', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(null, {status: 204}));
    vi.stubGlobal('fetch', fetchMock);

    await onRequest({
      env: {API_URL: 'https://backend.internal'},
      request: new Request('https://example.com/api/things'),
    });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Headers;
    expect(headers.has('x-proxy-secret')).toBe(false);
  });
});
