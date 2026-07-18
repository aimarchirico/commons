// Cloudflare Pages Function that reverse-proxies `/api/*` requests to the
// backend defined by the `API_URL` environment variable. Consumer repos re-export
// this from `functions/api/[[path]].js`:
//
//   export { onRequest } from '@aimarchirico/commons-cloudflare/proxy';
/**
 * @param {{env: {API_URL?: string, PROXY_SECRET?: string}, request: Request}} context
 */
export async function onRequest(context) {
  const apiUrl = context.env.API_URL;

  if (!apiUrl) {
    return new Response('API_URL not configured', {status: 500});
  }

  const url = new URL(context.request.url);
  const apiPath = url.pathname.replace(/^\/api/, '');
  const backendUrl = `${apiUrl}${apiPath}${url.search}`;

  const headers = new Headers(context.request.headers);
  headers.delete('host');

  headers.set('X-Forwarded-Prefix', '/api');
  headers.set('X-Forwarded-Host', url.host);
  headers.set('X-Forwarded-Proto', url.protocol.replace(':', ''));
  if (context.env.PROXY_SECRET) {
    headers.set('X-Proxy-Secret', context.env.PROXY_SECRET);
  }

  const response = await fetch(backendUrl, {
    method: context.request.method,
    headers: headers,
    body: context.request.body,
  });

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers,
  });
}
