import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import fs from 'fs';
import EventEmitter from 'events';
import type {IncomingMessage, ClientRequest} from 'http';

vi.mock('@aimarchirico/commons-project', () => ({
  resolveTool: vi.fn().mockReturnValue('/mock/tool/path'),
  runStreamed: vi.fn().mockReturnValue(0),
}));

const {httpGet} = vi.hoisted(() => ({httpGet: vi.fn()}));
vi.mock('http', () => ({default: {get: httpGet}}));

function mockHttpGet(statusCode: number, body?: string, error?: Error) {
  const mockReq = new EventEmitter() as unknown as ClientRequest;
  const mockRes = new EventEmitter() as unknown as IncomingMessage;
  mockRes.statusCode = statusCode;

  httpGet.mockImplementation(
    (
      _url: string | URL,
      _options: unknown,
      callback?: (res: IncomingMessage) => void,
    ): ClientRequest => {
      if (error) {
        setImmediate(() => mockReq.emit('error', error));
        return mockReq;
      }
      if (callback) {
        callback(mockRes);
      }
      if (statusCode === 200) {
        mockRes.emit('data', body ?? '{"openapi":"3.0.0"}');
        mockRes.emit('end');
      }
      return mockReq;
    },
  );
}

describe('generate-client.ts', () => {
  const originalEnv = process.env;

  beforeEach(async () => {
    vi.restoreAllMocks();
    httpGet.mockReset();
    const projectModule = await import('@aimarchirico/commons-project');
    vi.mocked(projectModule.runStreamed).mockReset().mockReturnValue(0);
    process.env = {...originalEnv};
    delete process.env.API_URL;
    delete process.env.CF_ACCESS_CLIENT_ID;
    delete process.env.CF_ACCESS_CLIENT_SECRET;
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('skips API generation if API_URL is not set', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    const {runGenerateClient} = await import('../generate-client.js');

    await runGenerateClient();

    expect(logSpy).toHaveBeenCalledWith(
      'API_URL not set, skipping API generation.',
    );
  });

  it('fetches spec, generates client and docs successfully', async () => {
    process.env.API_URL = 'http://example.com/spec';
    vi.spyOn(fs, 'writeFileSync').mockImplementation(() => {});
    vi.spyOn(fs, 'unlinkSync').mockImplementation(() => {});
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    mockHttpGet(200);
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

    const {runGenerateClient} = await import('../generate-client.js');
    await runGenerateClient();

    expect(logSpy).toHaveBeenCalledWith('Done.');
  });

  it('exits with code 2 when fetching the spec fails with a bad status', async () => {
    process.env.API_URL = 'http://example.com/spec';
    mockHttpGet(404);
    const exitSpy = vi
      .spyOn(process, 'exit')
      .mockImplementation((code?: string | number | null | undefined) => {
        throw new Error(`process.exit(${code})`);
      });
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const {runGenerateClient} = await import('../generate-client.js');
    await expect(runGenerateClient()).rejects.toThrow('process.exit(2)');

    expect(errorSpy).toHaveBeenCalledWith(
      'API generation failed:',
      'Failed to fetch spec: 404',
    );
    expect(exitSpy).toHaveBeenCalledWith(2);
  });

  it('exits with code 2 when the spec request errors', async () => {
    process.env.API_URL = 'http://example.com/spec';
    mockHttpGet(0, undefined, new Error('Network error'));
    const exitSpy = vi
      .spyOn(process, 'exit')
      .mockImplementation((code?: string | number | null | undefined) => {
        throw new Error(`process.exit(${code})`);
      });
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const {runGenerateClient} = await import('../generate-client.js');
    await expect(runGenerateClient()).rejects.toThrow('process.exit(2)');

    expect(errorSpy).toHaveBeenCalledWith(
      'API generation failed:',
      'Network error',
    );
    expect(exitSpy).toHaveBeenCalledWith(2);
  });

  it('exits with code 2 when client generation fails', async () => {
    process.env.API_URL = 'http://example.com/spec';
    vi.spyOn(fs, 'writeFileSync').mockImplementation(() => {});
    mockHttpGet(200);
    const projectModule = await import('@aimarchirico/commons-project');
    vi.mocked(projectModule.runStreamed).mockReturnValueOnce(1);
    const exitSpy = vi
      .spyOn(process, 'exit')
      .mockImplementation((code?: string | number | null | undefined) => {
        throw new Error(`process.exit(${code})`);
      });
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const {runGenerateClient} = await import('../generate-client.js');
    await expect(runGenerateClient()).rejects.toThrow('process.exit(2)');

    expect(errorSpy).toHaveBeenCalledWith(
      'API generation failed:',
      'openapi-generator-cli exited with status 1.',
    );
    expect(exitSpy).toHaveBeenCalledWith(2);
  });

  it('exits with code 2 when doc generation fails', async () => {
    process.env.API_URL = 'http://example.com/spec';
    vi.spyOn(fs, 'writeFileSync').mockImplementation(() => {});
    vi.spyOn(fs, 'existsSync').mockReturnValue(false);
    vi.spyOn(fs, 'mkdirSync').mockImplementation(() => undefined);
    mockHttpGet(200);
    const projectModule = await import('@aimarchirico/commons-project');
    vi.mocked(projectModule.runStreamed)
      .mockReturnValueOnce(0)
      .mockReturnValueOnce(1);
    const exitSpy = vi
      .spyOn(process, 'exit')
      .mockImplementation((code?: string | number | null | undefined) => {
        throw new Error(`process.exit(${code})`);
      });
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const {runGenerateClient} = await import('../generate-client.js');
    await expect(runGenerateClient()).rejects.toThrow('process.exit(2)');

    expect(errorSpy).toHaveBeenCalledWith(
      'API generation failed:',
      'swagger-markdown exited with status 1.',
    );
    expect(exitSpy).toHaveBeenCalledWith(2);
  });
});
