#!/usr/bin/env node

import {resolveTool, runStreamed} from '@aimarchirico/commons-project';
import path from 'path';
import fs from 'fs';
import os from 'os';
import https from 'https';
import http from 'http';
import {
  buildAccessHeaders,
  buildSpecUrl,
  resolveDocsDir,
  resolveOutputDir,
  toGeneratorSpecPath,
} from '../services/openapi-client';

const apiUrl = process.env.API_URL;
if (!apiUrl) {
  console.log('API_URL not set, skipping API generation.');
  process.exit(0);
}

const cfClientId = process.env.CF_ACCESS_CLIENT_ID;
const cfClientSecret = process.env.CF_ACCESS_CLIENT_SECRET;

async function fetchSpec(): Promise<string> {
  const specUrl = buildSpecUrl(apiUrl as string);
  const headers = buildAccessHeaders(cfClientId, cfClientSecret);
  if (Object.keys(headers).length) {
    console.log('Using Cloudflare Access service token');
  }

  return new Promise((resolve, reject) => {
    const client = specUrl.startsWith('https') ? https : http;
    const req = client.get(specUrl, {headers}, res => {
      if (res.statusCode !== 200) {
        reject(new Error(`Failed to fetch spec: ${res.statusCode}`));
        return;
      }
      let data = '';
      res.on('data', chunk => (data += chunk));
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
  });
}

function generateClient(specPath: string): void {
  console.log('Generating API client...');
  const outputDir = resolveOutputDir(process.env.API_CLIENT_OUTPUT_DIR);
  const safeSpecPath = toGeneratorSpecPath(specPath);

  const generator = resolveTool({
    from: import.meta.url,
    package: '@openapitools/openapi-generator-cli',
    bin: 'openapi-generator-cli',
    installHint: 'Run "pnpm install" to restore it.',
  });

  fs.rmSync(outputDir, {recursive: true, force: true});
  const status = runStreamed(generator, [
    'generate',
    '-i',
    safeSpecPath,
    '-g',
    'typescript-axios',
    '-o',
    outputDir,
  ]);
  if (status !== 0) {
    throw new Error(`openapi-generator-cli exited with status ${status}.`);
  }
  console.log(`OpenAPI client generated at ${outputDir}`);
}

function generateDocs(specPath: string): void {
  console.log('Generating API documentation...');
  const docsDir = resolveDocsDir(process.env.API_DOCS_OUTPUT_DIR);
  if (!fs.existsSync(docsDir)) {
    fs.mkdirSync(docsDir, {recursive: true});
  }

  const outputPath = path.resolve(docsDir, 'API.md');

  const markdown = resolveTool({
    from: import.meta.url,
    package: 'swagger-markdown',
    bin: 'swagger-markdown',
    installHint: 'Run "pnpm install" to restore it.',
  });

  const status = runStreamed(markdown, ['-i', specPath, '-o', outputPath]);
  if (status !== 0) {
    throw new Error(`swagger-markdown exited with status ${status}.`);
  }
  console.log(`OpenAPI documentation generated at ${outputPath}`);
}

async function main(): Promise<void> {
  try {
    console.log('Fetching OpenAPI spec from', apiUrl);
    const spec = await fetchSpec();
    const specPath = path.resolve(os.tmpdir(), 'openapi-spec.json');
    fs.writeFileSync(specPath, spec);

    generateClient(specPath);
    generateDocs(specPath);

    fs.unlinkSync(specPath);
    console.log('Done.');
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : String(e);
    console.error('API generation failed:', errorMsg);
    process.exit(2);
  }
}

void main();
