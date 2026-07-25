const names = (list: string): string[] =>
  list
    .split(/[,\s]+/)
    .map(name => name.trim())
    .filter(Boolean);

/**
 * Parse an environment-scoped assignment list of the form
 * `web-production=APP_URL,ACCOUNT_ID;api-production=VPS_HOST`, where the
 * right-hand side names the environment variables holding the values.
 */
export const parseEnvironmentScopes = (
  list: string | undefined,
): Array<{environment: string; names: string[]}> =>
  (list ?? '')
    .split(';')
    .map(group => group.trim())
    .filter(Boolean)
    .map(group => {
      const separator = group.indexOf('=');
      if (separator < 1) {
        throw new Error(
          `Malformed environment scope "${group}". Expected "<environment>=<NAME>,<NAME>".`,
        );
      }
      return {
        environment: group.slice(0, separator).trim(),
        names: names(group.slice(separator + 1)),
      };
    })
    .filter(scope => scope.names.length);

export const parseNames = (list: string | undefined): string[] =>
  names(list ?? '');
