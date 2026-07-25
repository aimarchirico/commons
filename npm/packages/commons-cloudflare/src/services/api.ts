const BASE = 'https://api.cloudflare.com/client/v4';

type Envelope<T> = {
  success: boolean;
  errors?: Array<{code: number; message: string}>;
  result: T;
};

export type Api = {
  get: <T>(path: string) => Promise<T | undefined>;
  send: <T>(
    method: 'POST' | 'PATCH' | 'PUT' | 'DELETE',
    path: string,
    body?: unknown,
  ) => Promise<T>;
};

/**
 * Minimal Cloudflare REST client. A missing resource resolves to undefined so
 * a command can distinguish "absent" from "failed".
 */
export const api = (token: string): Api => {
  const request = async (
    method: string,
    path: string,
    body?: unknown,
  ): Promise<{status: number; payload: Envelope<unknown>}> => {
    const response = await fetch(`${BASE}${path}`, {
      method,
      headers: {
        authorization: `Bearer ${token}`,
        'content-type': 'application/json',
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const text = await response.text();
    let payload: Envelope<unknown>;
    try {
      payload = JSON.parse(text) as Envelope<unknown>;
    } catch {
      throw new Error(`${method} ${path} returned ${response.status}: ${text}`);
    }
    return {status: response.status, payload};
  };

  const describe = (path: string, payload: Envelope<unknown>): string =>
    `${path} failed: ${
      payload.errors
        ?.map(error => `${error.code} ${error.message}`)
        .join('; ') || 'unknown Cloudflare error'
    }`;

  return {
    get: async <T>(path: string): Promise<T | undefined> => {
      const {status, payload} = await request('GET', path);
      if (status === 404) return undefined;
      if (!payload.success) throw new Error(describe(path, payload));
      return payload.result as T;
    },
    send: async <T>(
      method: 'POST' | 'PATCH' | 'PUT' | 'DELETE',
      path: string,
      body?: unknown,
    ): Promise<T> => {
      const {payload} = await request(method, path, body);
      if (!payload.success) throw new Error(describe(path, payload));
      return payload.result as T;
    },
  };
};
