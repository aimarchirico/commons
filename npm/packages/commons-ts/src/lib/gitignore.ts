import {execFileSync} from 'node:child_process';

/**
 * Lists paths `git` ignores under `cwd`, formatted as ESLint glob patterns.
 * Directory entries get a trailing `**` so the pattern also matches
 * everything beneath them. Returns an empty array if `git` is unavailable or
 * the command fails (e.g. outside a git repository).
 *
 * @param cwd - The directory to run `git ls-files` from.
 * @returns The gitignored paths, as ESLint `ignores` glob patterns.
 */
const gitignored = (cwd: string): string[] => {
  try {
    return execFileSync(
      'git',
      [
        'ls-files',
        '-z',
        '--others',
        '--ignored',
        '--exclude-standard',
        '--directory',
      ],
      {cwd, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024},
    )
      .split('\0')
      .filter(Boolean)
      .map(entry => (entry.endsWith('/') ? `${entry}**` : entry));
  } catch {
    return [];
  }
};

const ignores = gitignored(process.cwd());

/**
 * An ESLint flat config array ignoring every gitignored path, or an empty
 * array if there are none (or `git` is unavailable), so callers can always
 * spread this into their config without conditionals.
 */
export const gitignoreConfig = ignores.length ? [{ignores}] : [];
