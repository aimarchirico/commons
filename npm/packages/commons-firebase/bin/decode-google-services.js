#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const base64 = process.env.GOOGLE_SERVICES_JSON_BASE64;
const outputPath = process.argv[2] || 'src/assets/google-services.json';

if (!base64) {
  console.log('GOOGLE_SERVICES_JSON_BASE64 not set, skipping google-services.json.');
  process.exit(0);
}

fs.mkdirSync(path.dirname(outputPath), {recursive: true});
fs.writeFileSync(outputPath, Buffer.from(base64, 'base64').toString('utf-8'));
console.log(`Wrote ${outputPath}`);
