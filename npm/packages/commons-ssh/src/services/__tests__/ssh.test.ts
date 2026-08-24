import {beforeEach, describe, expect, it, vi} from 'vitest';
import {scpFiles, sshRun} from '../ssh.js';

const {run, runStreamed} = vi.hoisted(() => ({
  run: vi.fn(),
  runStreamed: vi.fn(),
}));
vi.mock('@aimarchirico/commons-project', () => ({run, runStreamed}));

const target = {host: 'vps.example.com', user: 'deploy', keyFile: '/keys/id'};

beforeEach(() => {
  run.mockReset();
  runStreamed.mockReset();
});

describe('sshRun', () => {
  it('runs the command over ssh with the target credentials', () => {
    run.mockReturnValue({status: 0, stdout: 'ok', stderr: ''});

    const result = sshRun(target, 'echo hi');

    expect(run).toHaveBeenCalledWith(
      'ssh',
      [
        '-i',
        '/keys/id',
        '-o',
        'StrictHostKeyChecking=accept-new',
        'deploy@vps.example.com',
        'echo hi',
      ],
      undefined,
    );
    expect(result).toEqual({status: 0, stdout: 'ok', stderr: ''});
  });

  it('passes input through to the remote command', () => {
    run.mockReturnValue({status: 0, stdout: '', stderr: ''});

    sshRun(target, 'cat > file', 'contents');

    expect(run).toHaveBeenCalledWith(
      'ssh',
      expect.arrayContaining(['cat > file']),
      'contents',
    );
  });
});

describe('scpFiles', () => {
  it('copies local files to the remote directory with streamed output', () => {
    runStreamed.mockReturnValue(0);

    const status = scpFiles(target, ['a.txt', 'b.txt'], '~/docker/app');

    expect(runStreamed).toHaveBeenCalledWith('scp', [
      '-i',
      '/keys/id',
      '-o',
      'StrictHostKeyChecking=accept-new',
      'a.txt',
      'b.txt',
      'deploy@vps.example.com:~/docker/app/',
    ]);
    expect(status).toBe(0);
  });
});
