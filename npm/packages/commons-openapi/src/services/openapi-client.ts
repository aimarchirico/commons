import path from 'path';

/**
 * Build the OpenAPI v3 spec URL for an API base URL.
 * @param apiUrl The API base URL.
 * @returns The spec document URL.
 */
export function buildSpecUrl(apiUrl: string): string {
  return `${apiUrl}/v3/api-docs`;
}

/**
 * Build the Cloudflare Access service token headers, when both halves of the
 * credential are present.
 * @param clientId The Cloudflare Access client ID.
 * @param clientSecret The Cloudflare Access client secret.
 * @returns The headers to send, empty when either half is missing.
 */
export function buildAccessHeaders(
  clientId: string | undefined,
  clientSecret: string | undefined,
): Record<string, string> {
  return clientId && clientSecret
    ? {
        'CF-Access-Client-Id': clientId,
        'CF-Access-Client-Secret': clientSecret,
      }
    : {};
}

/**
 * Resolve the directory the generated client is written to.
 * @param override The `API_CLIENT_OUTPUT_DIR` environment value, if set.
 * @returns The resolved output directory.
 */
export function resolveOutputDir(override: string | undefined): string {
  return path.resolve(
    override || path.resolve(process.cwd(), 'src/services/generated'),
  );
}

/**
 * Resolve the directory the generated documentation is written to.
 * @param override The `API_DOCS_OUTPUT_DIR` environment value, if set.
 * @returns The resolved documentation directory.
 */
export function resolveDocsDir(override: string | undefined): string {
  return path.resolve(override || path.resolve(process.cwd(), 'docs'));
}

/**
 * Normalise a filesystem path into the forward-slash form the OpenAPI
 * generator's `-i` flag expects, since it otherwise misparses Windows-style
 * backslashes as escape sequences.
 * @param specPath The filesystem path to the downloaded spec.
 * @returns The normalised path.
 */
export function toGeneratorSpecPath(specPath: string): string {
  return specPath.replace(/\\/g, '/');
}
