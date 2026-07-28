import {spawnSync} from 'child_process';
import {fail} from './report.js';

export type CliResult = {status: number; stdout: string; stderr: string};

/**
 * Run an external CLI resolved from `PATH`. These are one-shot provisioning
 * tools, so a globally installed CLI is the contract rather than a dependency
 * every consumer of the package would otherwise have to carry.
 */
export const run = (
  command: string,
  args: string[],
  input?: string,
): CliResult => {
  const result = spawnSync(command, args, {
    encoding: 'utf8',
    input,
    shell: process.platform === 'win32',
  });
  if (result.error) {
    throw new Error(`Could not run "${command}": ${result.error.message}.`);
  }
  return {
    status: result.status ?? 1,
    stdout: (result.stdout ?? '').trim(),
    stderr: (result.stderr ?? '').trim(),
  };
};

export const runOrThrow = (
  command: string,
  args: string[],
  input?: string,
): string => {
  const result = run(command, args, input);
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(' ')} failed:\n${result.stderr}`);
  }
  return result.stdout;
};

export const runJson = <T>(command: string, args: string[]): T =>
  JSON.parse(runOrThrow(command, args)) as T;

const VERSION = /(\d+)\.(\d+)\.(\d+)/;

const parseVersion = (text: string): number[] | undefined => {
  const match = VERSION.exec(text);
  return match
    ? [Number(match[1]), Number(match[2]), Number(match[3])]
    : undefined;
};

const isBelow = (found: number[], minimum: number[]): boolean => {
  for (let index = 0; index < minimum.length; index += 1) {
    const left = found[index] ?? 0;
    const right = minimum[index] ?? 0;
    if (left !== right) return left < right;
  }
  return false;
};

/**
 * Assert an external CLI is installed and recent enough. The output these
 * commands parse is version-specific, so a floor turns a confusing parse
 * failure further in into a message naming exactly what to install.
 */
export const requireCli = (
  command: string,
  options: {
    minVersion: string;
    installHint: string;
    versionArgs?: string[];
  },
): void => {
  let result: CliResult;
  try {
    result = run(command, options.versionArgs ?? ['--version']);
  } catch {
    fail(`"${command}" is not on PATH. ${options.installHint}`);
  }
  if (result.status !== 0) {
    fail(`"${command}" is installed but not usable. ${options.installHint}`);
  }

  const minimum = parseVersion(options.minVersion);
  const found = parseVersion(`${result.stdout}\n${result.stderr}`);
  if (!minimum || !found) return;

  if (isBelow(found, minimum)) {
    fail(
      `"${command}" ${found.join('.')} is older than the required ${options.minVersion}. ${options.installHint}`,
    );
  }
};
