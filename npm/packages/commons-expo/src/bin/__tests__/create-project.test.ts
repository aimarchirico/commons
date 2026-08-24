import {
  fail,
  printSummary,
  report,
  resolveTool,
  runJson,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {createProject} from '../create-project.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveTool: vi.fn(),
  runJson: vi.fn(),
  writeOutputs: vi.fn(),
}));

describe('create-project.ts', () => {
  beforeEach(() => {
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveTool).mockClear();
    vi.mocked(resolveTool).mockReturnValue('eas');
    vi.mocked(runJson).mockClear();
    vi.mocked(writeOutputs).mockClear();
  });

  it('reports created and writes the project id for a new project', () => {
    vi.mocked(runJson).mockReturnValue({
      status: 'created',
      projectId: 'proj-1',
      owner: 'my-owner',
      slug: 'my-app',
      dashboardUrl: 'https://expo.dev',
    });

    createProject();

    expect(report).toHaveBeenCalledWith(
      'eas project my-owner/my-app',
      'created',
      'proj-1',
    );
    expect(writeOutputs).toHaveBeenCalledWith({EAS_PROJECT_ID: 'proj-1'});
    expect(printSummary).toHaveBeenCalledWith('commons-expo create-project');
  });

  it('reports present for an already-linked project', () => {
    vi.mocked(runJson).mockReturnValue({
      status: 'noop',
      projectId: 'proj-1',
      owner: 'my-owner',
      slug: 'my-app',
      dashboardUrl: 'https://expo.dev',
    });

    createProject();

    expect(report).toHaveBeenCalledWith(
      'eas project my-owner/my-app',
      'present',
      'proj-1',
    );
  });

  it('catches non-Error exceptions and calls fail', () => {
    vi.mocked(runJson).mockImplementation(() => {
      throw 'boom';
    });

    expect(() => createProject()).toThrow('fail: boom');
    expect(fail).toHaveBeenCalledWith('boom');
  });
});
