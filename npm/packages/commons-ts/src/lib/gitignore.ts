import {execFileSync} from 'node:child_process';

function listGitignoredAsEslintPatterns(cwd: string): string[] {
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
}

const ignores = listGitignoredAsEslintPatterns(process.cwd());

/**
 * An ESLint flat config array ignoring every gitignored path, or an empty
 * array if there are none (or `git` is unavailable), so callers can always
 * spread this into their config without conditionals.
 */
export const gitignoreConfig = ignores.length ? [{ignores}] : [];
