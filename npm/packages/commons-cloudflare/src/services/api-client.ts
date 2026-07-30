import {context, fail} from '@aimarchirico/commons-project';

const BASE = 'https://api.cloudflare.com/client/v4';

type Envelope<T> = {
  success: boolean;
  errors?: Array<{code: number; message: string}>;
  result: T;
};

/** A minimal Cloudflare REST client, as returned by {@link api}. */
export type ApiClient = {
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
 * @param token
 * @returns A Cloudflare API client.
 */
export const api = (token: string): ApiClient => {
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

/**
 * The account to act in. A token scoped to exactly one account already names
 * it, so the override only has to settle the ambiguous case — and an ambiguous
 * case fails rather than picking, since the wrong account is not a mistake a
 * re-run corrects.
 * @param client
 * @param override
 * @returns The resolved account ID.
 */
export const resolveAccount = async (
  client: ApiClient,
  override?: string,
): Promise<string> => {
  if (override) {
    context('cloudflare account', override, 'from CLOUDFLARE_ACCOUNT_ID');
    return override;
  }

  const accounts =
    (await client.get<Array<{id: string; name: string}>>('/accounts')) ?? [];
  if (!accounts.length) {
    fail(
      'The Cloudflare token can see no accounts. Check CLOUDFLARE_API_TOKEN, or set CLOUDFLARE_ACCOUNT_ID.',
    );
  }
  if (accounts.length > 1) {
    const names = accounts
      .map(account => `  - ${account.name} (${account.id})`)
      .join('\n');
    fail(
      `The Cloudflare token can see ${accounts.length} accounts. Set CLOUDFLARE_ACCOUNT_ID to one of:\n${names}`,
    );
  }
  context(
    'cloudflare account',
    `${accounts[0].name} (${accounts[0].id})`,
    'derived — the token sees one account',
  );
  return accounts[0].id;
};
