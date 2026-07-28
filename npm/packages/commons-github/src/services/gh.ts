import {
  context,
  requireCli,
  run,
  runJson as runCliJson,
  runOrThrow as runCliOrThrow,
} from '@aimarchirico/commons-project';
import type {CliResult} from '@aimarchirico/commons-project';

export type GhResult = CliResult;

const INSTALL_HINT =
  'Install the GitHub CLI (https://cli.github.com) and authenticate it with "gh auth login".';

/**
 * Assert the CLI is present and recent enough. These commands parse the output
 * of `gh project` and `gh repo view --json`, whose shapes have moved between
 * releases, so an old CLI fails here rather than as a confusing parse error
 * further in.
 */
export const requireGh = (): void => {
  requireCli('gh', {minVersion: '2.40.0', installHint: INSTALL_HINT});
};

export const gh = (args: string[], input?: string): GhResult => {
  try {
    return run('gh', args, input);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`${message} ${INSTALL_HINT}`);
  }
};

export const ghOrThrow = (args: string[], input?: string): string =>
  runCliOrThrow('gh', args, input);

export const ghJson = <T>(args: string[]): T => runCliJson<T>('gh', args);

/**
 * Read a REST resource, returning undefined when it does not exist so a
 * command can distinguish "absent" from "failed".
 */
export const apiGet = <T>(endpoint: string): T | undefined => {
  const result = gh(['api', endpoint]);
  if (result.status !== 0) {
    if (/HTTP 404/.test(result.stderr)) return undefined;
    throw new Error(`gh api ${endpoint} failed:\n${result.stderr}`);
  }
  return JSON.parse(result.stdout) as T;
};

export const apiWrite = (
  method: 'POST' | 'PATCH' | 'PUT',
  endpoint: string,
  fields: Record<string, string> = {},
): void => {
  const args = ['api', '--method', method, endpoint, '--silent'];
  for (const [name, value] of Object.entries(fields)) {
    args.push('-f', `${name}=${value}`);
  }
  ghOrThrow(args);
};

/**
 * Resolve the target repository from `GITHUB_REPOSITORY`, falling back to the
 * repository of the working directory. The resolved value is reported, because
 * a derivation made from the wrong directory writes to the wrong repository
 * and nothing else in the output would say so.
 */
export const repoContext = (): {owner: string; repo: string; slug: string} => {
  requireGh();

  const fromEnv = process.env.GITHUB_REPOSITORY;
  if (fromEnv?.includes('/')) {
    const [owner, repo] = fromEnv.split('/');
    context('repository', `${owner}/${repo}`, 'from GITHUB_REPOSITORY');
    return {owner, repo, slug: `${owner}/${repo}`};
  }

  const data = ghJson<{owner: {login: string}; name: string}>([
    'repo',
    'view',
    '--json',
    'owner,name',
  ]);
  const slug = `${data.owner.login}/${data.name}`;
  context('repository', slug, 'derived from the working directory');
  return {owner: data.owner.login, repo: data.name, slug};
};
