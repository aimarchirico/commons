#!/usr/bin/env node

import shell from 'shelljs';
import replace from 'replace-in-file';

// Cloudflare Pages rejects upload paths containing "node_modules", so rename
// the exported directory and rewrite references to it. Run from the app
// directory that holds the exported `dist/`.
if (shell.test('-d', 'dist/assets/node_modules')) {
  shell.mv('dist/assets/node_modules', 'dist/assets/nodemodules');
  replace.sync({
    files: 'dist/**/*',
    from: /assets\/node_modules/g,
    to: 'assets/nodemodules',
  });
}
