import {spawnSync} from 'child_process';

export type GhResult = {status: number; stdout: string; stderr: string};

export const gh = (args: string[], input?: string): GhResult => {
  const result = spawnSync('gh', args, {
    encoding: 'utf8',
    input,
    shell: process.platform === 'win32',
  });
  if (result.error) {
    throw new Error(
      `Could not run "gh ${args[0]}": ${result.error.message}. Install the GitHub CLI and authenticate it.`,
    );
  }
  return {
    status: result.status ?? 1,
    stdout: (result.stdout ?? '').trim(),
    stderr: (result.stderr ?? '').trim(),
  };
};

export const ghOrThrow = (args: string[], input?: string): string => {
  const result = gh(args, input);
  if (result.status !== 0) {
    throw new Error(`gh ${args.join(' ')} failed:\n${result.stderr}`);
  }
  return result.stdout;
};

export const ghJson = <T>(args: string[]): T =>
  JSON.parse(ghOrThrow(args)) as T;

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
 * repository of the working directory.
 */
export const repoContext = (): {owner: string; repo: string; slug: string} => {
  const fromEnv = process.env.GITHUB_REPOSITORY;
  if (fromEnv?.includes('/')) {
    const [owner, repo] = fromEnv.split('/');
    return {owner, repo, slug: `${owner}/${repo}`};
  }
  const data = ghJson<{owner: {login: string}; name: string}>([
    'repo',
    'view',
    '--json',
    'owner,name',
  ]);
  return {
    owner: data.owner.login,
    repo: data.name,
    slug: `${data.owner.login}/${data.name}`,
  };
};
