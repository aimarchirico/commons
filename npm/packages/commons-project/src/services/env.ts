type Resolved<R extends readonly string[], O extends readonly string[]> = {
  [K in R[number]]: string;
} & {
  [K in O[number]]?: string;
};

const read = (name: string): string | undefined => {
  const value = process.env[name];
  return value === undefined || value.trim() === '' ? undefined : value;
};

/**
 * Resolve environment variables, reporting every missing required variable at
 * once instead of failing on the first one. Optional variables that are unset
 * or empty resolve to `undefined`.
 * @param required
 * @param optional
 * @returns The resolved environment variables object.
 */
export const resolveEnv = <
  const R extends readonly string[],
  const O extends readonly string[] = [],
>(
  required: R,
  optional?: O,
): Resolved<R, O> => {
  const resolved: Record<string, string | undefined> = {};
  const missing: string[] = [];

  for (const name of required) {
    const value = read(name);
    if (value === undefined) {
      missing.push(name);
    } else {
      resolved[name] = value;
    }
  }

  if (missing.length) {
    const list = missing.map(name => `  - ${name}`).join('\n');
    console.error(
      `Missing required environment ${
        missing.length === 1 ? 'variable' : 'variables'
      }:\n${list}`,
    );
    process.exit(1);
  }

  for (const name of optional ?? []) {
    resolved[name] = read(name);
  }

  return resolved as Resolved<R, O>;
};

/**
 * Collect the variables of `names` that are set, so a caller can push a subset
 * of a documented surface without writing empty values over working ones.
 * @param names
 * @returns The collected environment variables.
 */
export const collectEnv = (
  names: readonly string[],
): Record<string, string> => {
  const present: Record<string, string> = {};
  for (const name of names) {
    const value = read(name);
    if (value !== undefined) present[name] = value;
  }
  return present;
};

/**
 * Read the variables named by a `KEY=KEY2` style list, so a caller can pass an
 * arbitrary, caller-owned set of variables through a single variable.
 * @param list
 * @returns The resolved key-value environment variables.
 */
export const resolveEnvList = (list: string): Record<string, string> =>
  collectEnv(
    list
      .split(/[,\s]+/)
      .map(name => name.trim())
      .filter(Boolean),
  );
