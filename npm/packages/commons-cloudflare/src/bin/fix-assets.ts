#!/usr/bin/env node

import shell from 'shelljs';
import {replaceInFileSync} from 'replace-in-file';

if (shell.test('-d', 'dist/assets/node_modules')) {
  shell.mv('dist/assets/node_modules', 'dist/assets/nodemodules');
  replaceInFileSync({
    files: 'dist/**/*',
    from: /assets\/node_modules/g,
    to: 'assets/nodemodules',
  });
}
