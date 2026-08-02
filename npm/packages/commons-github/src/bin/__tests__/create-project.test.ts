import {fail, printSummary, report} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {createProject} from '../create-project.js';
import {gh, ghJson, ghOrThrow, repoContext} from '../../services/gh.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
}));

vi.mock('../../services/gh.js', () => ({
  gh: vi.fn(),
  ghJson: vi.fn(),
  ghOrThrow: vi.fn(),
  repoContext: vi.fn(),
}));

describe('create-project.ts', () => {
  beforeEach(() => {
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(gh).mockClear();
    vi.mocked(gh).mockReturnValue({
      status: 0,
      stdout: JSON.stringify({projects: []}),
      stderr: '',
    });
    vi.mocked(ghJson).mockClear();
    vi.mocked(ghJson).mockReturnValue({projectsV2: {nodes: []}});
    vi.mocked(ghOrThrow).mockClear();
    vi.mocked(repoContext).mockClear();

    vi.mocked(repoContext).mockReturnValue({
      owner: 'my-owner',
      repo: 'my-repo',
      slug: 'my-owner/my-repo',
    });
  });

  it('reports present if project is already linked (using nodes)', () => {
    vi.mocked(ghJson).mockReturnValue({
      projectsV2: {
        nodes: [{number: 42, title: 'My Repo'}],
      },
    });

    createProject();

    expect(report).toHaveBeenCalledWith(
      'project "My Repo"',
      'present',
      '#42 linked to my-owner/my-repo',
    );
    expect(printSummary).toHaveBeenCalledWith('create-project');
  });

  it('reports present if project is already linked (using Nodes uppercase)', () => {
    vi.mocked(ghJson).mockReturnValue({
      projectsV2: {
        Nodes: [{number: 42, title: 'My Repo'}],
      },
    });

    createProject();

    expect(report).toHaveBeenCalledWith(
      'project "My Repo"',
      'present',
      '#42 linked to my-owner/my-repo',
    );
  });

  it('links an existing owned project when not yet linked', () => {
    vi.mocked(ghJson).mockReturnValue({projectsV2: {nodes: []}});
    vi.mocked(gh).mockReturnValue({
      status: 0,
      stdout: JSON.stringify({projects: [{number: 10, title: 'My Repo'}]}),
      stderr: '',
    });

    createProject();

    expect(ghOrThrow).toHaveBeenCalledWith([
      'project',
      'link',
      '10',
      '--owner',
      'my-owner',
      '-R',
      'my-owner/my-repo',
    ]);
    expect(report).toHaveBeenCalledWith(
      'project "My Repo"',
      'updated',
      '#10 linked',
    );
  });

  it('copies template project when neither linked nor existing owned project is found', () => {
    vi.mocked(ghJson).mockReturnValue({projectsV2: {nodes: []}});
    vi.mocked(gh).mockImplementation((args: string[]) => {
      const ownerIndex = args.indexOf('--owner');
      const owner = ownerIndex !== -1 ? args[ownerIndex + 1] : undefined;
      if (owner === 'my-owner') {
        return {status: 0, stdout: JSON.stringify({projects: []}), stderr: ''};
      }
      if (owner === 'aimarchirico') {
        return {
          status: 0,
          stdout: JSON.stringify({
            projects: [{number: 1, title: 'Commons Template'}],
          }),
          stderr: '',
        };
      }
      return {status: 1, stdout: '', stderr: ''};
    });

    vi.mocked(ghOrThrow).mockReturnValue(JSON.stringify({number: 99}));

    createProject();

    expect(ghOrThrow).toHaveBeenCalledWith([
      'project',
      'copy',
      '1',
      '--source-owner',
      'aimarchirico',
      '--target-owner',
      'my-owner',
      '--title',
      'My Repo',
      '--format',
      'json',
    ]);
    expect(report).toHaveBeenCalledWith(
      'project "My Repo"',
      'created',
      '#99 copied from aimarchirico/#1',
    );
  });

  it('fails if template source project is missing', () => {
    vi.mocked(ghJson).mockReturnValue({projectsV2: {nodes: []}});
    vi.mocked(gh).mockReturnValue({
      status: 0,
      stdout: JSON.stringify({projects: []}),
      stderr: '',
    });

    expect(() => createProject()).toThrow(
      'fail: Could not find a project titled "Commons Template" owned by aimarchirico to copy.',
    );
    expect(fail).toHaveBeenCalledWith(
      'Could not find a project titled "Commons Template" owned by aimarchirico to copy.',
    );
  });

  it('handles ownedProject gh command non-zero exit code', () => {
    vi.mocked(ghJson).mockReturnValue({projectsV2: {nodes: []}});
    vi.mocked(gh).mockReturnValue({status: 1, stdout: '', stderr: ''});

    expect(() => createProject()).toThrow(
      'fail: Could not find a project titled "Commons Template" owned by aimarchirico to copy.',
    );
  });

  it('catches non-Error exceptions and calls fail', () => {
    vi.mocked(ghJson).mockImplementation(() => {
      throw 12345;
    });

    expect(() => createProject()).toThrow('fail: 12345');
    expect(fail).toHaveBeenCalledWith('12345');
  });
});
