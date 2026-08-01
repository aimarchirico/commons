import fs from 'fs';
import path from 'path';
import {createRequire} from 'module';
import {spawnSync} from 'child_process';
import {fail} from './report.js';

/** The exit code and captured output of a finished command. */
export type CliResult = {status: number; stdout: string; stderr: string};

/**
 * Either a name to find on `PATH`, or a resolved executable carrying the name
 * to use when talking about it - `node /…/eas-cli/bin/run` should still be
 * reported as "eas".
 */
export type Command = string | {argv: string[]; name: string};

const argv = (command: Command): string[] =>
  typeof command === 'string' ? [command] : command.argv;

const name = (command: Command): string =>
  typeof command === 'string' ? command : command.name;

/**
 * Run a command and return its exit code and stdout/stderr output.
 * @param command The command name or command config.
 * @param args The arguments to pass.
 * @param input Optional stdin input.
 * @returns The command execution results.
 */
export const run = (
  command: Command,
  args: string[],
  input?: string,
): CliResult => {
  const [executable, ...prefix] = argv(command);
  const result = spawnSync(executable, [...prefix, ...args], {
    encoding: 'utf8',
    input,
    shell: process.platform === 'win32',
  });
  if (result.error) {
    throw new Error(
      `Could not run "${name(command)}": ${result.error.message}.`,
    );
  }
  return {
    status: result.status ?? 1,
    stdout: (result.stdout ?? '').trim(),
    stderr: (result.stderr ?? '').trim(),
  };
};

/**
 * Run a command and throw an error if the command fails (exit code not 0).
 * @param command The command name or command config.
 * @param args The arguments to pass.
 * @param input Optional stdin input.
 * @returns The stdout of the command.
 */
export const runOrThrow = (
  command: Command,
  args: string[],
  input?: string,
): string => {
  const result = run(command, args, input);
  if (result.status !== 0) {
    throw new Error(
      `${name(command)} ${args.join(' ')} failed:\n${result.stderr}`,
    );
  }
  return result.stdout;
};

/**
 * Run a command, throw if it fails, and parse the stdout as JSON.
 * @param command The command name or command config.
 * @param args The arguments to pass.
 * @returns The parsed JSON object of type T.
 */
export const runJson = <T>(command: Command, args: string[]): T =>
  JSON.parse(runOrThrow(command, args)) as T;

/**
 * Run a command with its streams attached to this process, for generators
 * whose progress output is the point. Nothing is captured, so the caller
 * learns only the exit status.
 * @param command
 * @param args
 * @returns The process exit status.
 */
export const runStreamed = (command: Command, args: string[]): number => {
  const [executable, ...prefix] = argv(command);
  const result = spawnSync(executable, [...prefix, ...args], {
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });
  if (result.error) {
    throw new Error(
      `Could not run "${name(command)}": ${result.error.message}.`,
    );
  }
  return result.status ?? 1;
};

/**
 * Locate an executable belonging to a package this one depends on, so the
 * version that runs is the one the lockfile pinned rather than whatever a
 * global install happened to leave on `PATH`. `from` is the calling module's
 * `import.meta.url`, since resolution has to start at the package that
 * declares the dependency.
 *
 * The script is invoked through the current Node binary rather than executed
 * directly, which sidesteps both the shebang and the executable bit.
 * @param from
 * @param packageName
 * @param binName
 * @returns The command arguments if resolved, otherwise undefined.
 */
export const packageBin = (
  from: string,
  packageName: string,
  binName: string,
): string[] | undefined => {
  try {
    const manifestPath = createRequire(from).resolve(
      `${packageName}/package.json`,
    );
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8')) as {
      bin?: string | Record<string, string>;
    };
    const entry =
      typeof manifest.bin === 'string' ? manifest.bin : manifest.bin?.[binName];
    if (!entry) return undefined;
    return [process.execPath, path.join(path.dirname(manifestPath), entry)];
  } catch {
    return undefined;
  }
};

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
 * Assert a CLI is usable and recent enough. The output these commands parse is
 * version-specific, so a floor turns a confusing parse failure further in into
 * a message naming exactly what to install.
 * @param command
 * @param options
 * @param options.minVersion
 * @param options.installHint
 * @param options.versionArgs
 */
export const requireCli = (
  command: Command,
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
    fail(`"${name(command)}" is not available. ${options.installHint}`);
  }
  if (result.status !== 0) {
    fail(`"${name(command)}" is not usable. ${options.installHint}`);
  }

  const minimum = parseVersion(options.minVersion);
  const found = parseVersion(`${result.stdout}\n${result.stderr}`);
  if (!minimum || !found) return;

  if (isBelow(found, minimum)) {
    fail(
      `"${name(command)}" ${found.join('.')} is older than the required ${options.minVersion}. ${options.installHint}`,
    );
  }
};

/**
 * Resolve a CLI a package depends on, preferring the copy the lockfile pinned.
 *
 * With `minVersion`, `PATH` is an accepted fallback and the version is
 * checked - the shape for a tool that may legitimately be installed globally.
 * Without it, resolution must succeed locally, since a declared dependency
 * that cannot be resolved means the install is incomplete rather than that the
 * tool lives elsewhere. Some generators also pay a real cost to answer
 * `--version`, which is reason enough not to ask them.
 * @param options
 * @param options.from
 * @param options.package
 * @param options.bin
 * @param options.minVersion
 * @param options.installHint
 * @returns The resolved command.
 */
export const resolveTool = (options: {
  from: string;
  package: string;
  bin: string;
  minVersion?: string;
  installHint: string;
}): Command => {
  const local = packageBin(options.from, options.package, options.bin);

  if (!options.minVersion) {
    if (!local) {
      fail(
        `"${options.bin}" could not be resolved from ${options.package}. ${options.installHint}`,
      );
    }
    return {argv: local, name: options.bin};
  }

  const command: Command = local
    ? {argv: local, name: options.bin}
    : options.bin;
  requireCli(command, {
    minVersion: options.minVersion,
    installHint: options.installHint,
  });
  return command;
};
