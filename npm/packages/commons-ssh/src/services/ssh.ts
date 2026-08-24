import {run, runStreamed} from '@aimarchirico/commons-project';

/** Connection details for an SSH/SCP target. */
export type SshTarget = {host: string; user: string; keyFile: string};

const sshArgs = (target: SshTarget): string[] => [
  '-i',
  target.keyFile,
  '-o',
  'StrictHostKeyChecking=accept-new',
];

/**
 * Run a command on the remote host over SSH.
 * @param target The connection details.
 * @param command The remote shell command to run.
 * @param input Optional stdin to pipe to the remote command.
 * @returns The exit status and captured output.
 */
export function sshRun(
  target: SshTarget,
  command: string,
  input?: string,
): {status: number; stdout: string; stderr: string} {
  // shell:false: ssh.exe is a real binary on every platform, so no shell is
  // needed to resolve it, and one must be avoided here regardless, since
  // cmd.exe parses `&&`/`>`/etc. in `command` before ssh ever sees it,
  // running fragments of the remote command locally on Windows.
  return run(
    'ssh',
    [...sshArgs(target), `${target.user}@${target.host}`, command],
    input,
    {shell: false},
  );
}

/**
 * Copy local files to a directory on the remote host, streaming scp's own
 * progress output.
 * @param target The connection details.
 * @param localFiles Paths of the local files to copy.
 * @param remoteDir The destination directory on the remote host.
 * @returns The scp process's exit status.
 */
export function scpFiles(
  target: SshTarget,
  localFiles: string[],
  remoteDir: string,
): number {
  return runStreamed(
    'scp',
    [
      ...sshArgs(target),
      ...localFiles,
      `${target.user}@${target.host}:${remoteDir}/`,
    ],
    {shell: false},
  );
}
