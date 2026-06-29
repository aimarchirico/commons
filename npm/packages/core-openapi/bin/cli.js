#!/usr/bin/env node

const {execSync} = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const https = require('https');
const http = require('http');

const packageRoot = path.resolve(__dirname, '..');

const apiUrl = process.env.API_URL;
if (!apiUrl) {
  console.log('API_URL not set, skipping API generation.');
  process.exit(0);
}

const cfClientId = process.env.CF_ACCESS_CLIENT_ID;
const cfClientSecret = process.env.CF_ACCESS_CLIENT_SECRET;

async function fetchSpec() {
  const specUrl = `${apiUrl}/v3/api-docs`;
  /** @type {Record<string, string>} */
  const headers = {};

  if (cfClientId && cfClientSecret) {
    console.log('Using Cloudflare Access service token');
    headers['CF-Access-Client-Id'] = cfClientId;
    headers['CF-Access-Client-Secret'] = cfClientSecret;
  }

  return new Promise((resolve, reject) => {
    const client = specUrl.startsWith('https') ? https : http;
    const req = client.get(specUrl, {headers}, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`Failed to fetch spec: ${res.statusCode}`));
        return;
      }
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
  });
}

/**
 * @param {string} specPath
 */
function generateClient(specPath) {
  console.log('Generating API client...');
  const outputDir =
    process.env.API_CLIENT_OUTPUT_DIR ||
    path.resolve(process.cwd(), 'src/generated');
  const cmd = `rm -rf "${outputDir}" && npx @openapitools/openapi-generator-cli generate -i "${specPath}" -g typescript-axios -o "${outputDir}"`;
  execSync(cmd, {stdio: 'inherit', cwd: packageRoot});
  console.log(`OpenAPI client generated at ${outputDir}`);
}

/**
 * @param {string} specPath
 */
function generateDocs(specPath) {
  console.log('Generating API documentation...');
  const docsDir =
    process.env.API_DOCS_OUTPUT_DIR || path.resolve(process.cwd(), 'docs');
  if (!fs.existsSync(docsDir)) {
    fs.mkdirSync(docsDir, {recursive: true});
  }

  const outputPath = path.resolve(docsDir, 'API.md');
  const cmd = `npx widdershins --code "${specPath}" -o "${outputPath}"`;
  execSync(cmd, {stdio: 'inherit', cwd: packageRoot});
  console.log(`OpenAPI documentation generated at ${outputPath}`);
}

async function main() {
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

main();
