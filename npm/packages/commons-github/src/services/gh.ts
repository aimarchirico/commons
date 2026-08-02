import {
  context,
  requireCli,
  run,
  runJson as runCliJson,
  runOrThrow as runCliOrThrow,
} from '@aimarchirico/commons-project';
import type {CliResult} from '@aimarchirico/commons-project';

/** The exit code and captured output of a finished `gh` invocation. */
export type GhResult = CliResult;

const INSTALL_HINT =
  'Install the GitHub CLI (https://cli.github.com) and authenticate it with "gh auth login".';

/**
 * Assert the CLI is present and recent enough. These commands parse the output
 * of `gh project` and `gh repo view --json`, whose shapes have moved between
 * releases, so an old CLI fails here rather than as a confusing parse error
 * further in.
 */
export function requireGh(): void {
  requireCli('gh', {minVersion: '2.40.0', installHint: INSTALL_HINT});
}

/**
 * Run a GitHub CLI command.
 * @param args The arguments to pass.
 * @param input Optional stdin input.
 * @returns The command execution results.
 */
export function gh(args: string[], input?: string): GhResult {
  try {
    return run('gh', args, input);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`${message} ${INSTALL_HINT}`);
  }
}

/**
 * Run a GitHub CLI command and throw if it fails.
 * @param args The arguments to pass.
 * @param input Optional stdin input.
 * @returns The stdout of the command.
 */
export function ghOrThrow(args: string[], input?: string): string {
  return runCliOrThrow('gh', args, input);
}

/**
 * Run a GitHub CLI command and parse the stdout as JSON.
 * @param args The arguments to pass.
 * @returns The parsed JSON object of type T.
 */
export function ghJson<T>(args: string[]): T {
  return runCliJson<T>('gh', args);
}

/**
 * Read a REST resource, returning undefined when it does not exist so a
 * command can distinguish "absent" from "failed".
 * @param endpoint
 * @returns The requested resource of type T, or undefined if it does not exist.
 */
export function apiGet<T>(endpoint: string): T | undefined {
  const result = gh(['api', endpoint]);
  if (result.status !== 0) {
    if (/HTTP 404/.test(result.stderr)) return undefined;
    throw new Error(`gh api ${endpoint} failed:\n${result.stderr}`);
  }
  return JSON.parse(result.stdout) as T;
}

/**
 * Write to a GitHub API endpoint.
 * @param method The HTTP method to use.
 * @param endpoint The API endpoint.
 * @param fields The fields to write.
 */
export function apiWrite(
  method: 'POST' | 'PATCH' | 'PUT',
  endpoint: string,
  fields: Record<string, string> = {},
): void {
  const args = ['api', '--method', method, endpoint, '--silent'];
  for (const [name, value] of Object.entries(fields)) {
    args.push('-f', `${name}=${value}`);
  }
  ghOrThrow(args);
}

/**
 * Resolve the target repository from the working directory. The resolved
 * value is reported, because a derivation made from the wrong directory
 * writes to the wrong repository and nothing else in the output would say so.
 * @returns The owner, repo name, and slug of the repository.
 */
export function repoContext(): {owner: string; repo: string; slug: string} {
  requireGh();

  const data = ghJson<{owner: {login: string}; name: string}>([
    'repo',
    'view',
    '--json',
    'owner,name',
  ]);
  const slug = `${data.owner.login}/${data.name}`;
  context('repository', slug, 'derived from the working directory');
  return {owner: data.owner.login, repo: data.name, slug};
}
