import {run} from './cli.js';

/**
 * The default branch of the repository in the working directory, read from the
 * remote HEAD the clone recorded. Returns undefined rather than guessing when
 * there is no remote to read, so a caller can fall back and say that it did.
 * @returns The default branch name, or undefined if no remote is configured.
 */
export const defaultBranch = (): string | undefined => {
  const result = run('git', [
    'symbolic-ref',
    '--short',
    'refs/remotes/origin/HEAD',
  ]);
  if (result.status !== 0) return undefined;
  return result.stdout.replace(/^origin\//, '') || undefined;
};
