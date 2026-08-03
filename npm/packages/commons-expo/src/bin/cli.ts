#!/usr/bin/env node

import {pathToFileURL} from 'url';

const commands: Record<string, () => Promise<void>> = {
  'build-android': async () => {
    const {buildAndroid} = await import('./build-android.js');
    buildAndroid();
  },
  'create-project': async () => {
    const {createProject} = await import('./create-project.js');
    createProject();
  },
  'import-keystore': async () => {
    const {importKeystore} = await import('./import-keystore.js');
    importKeystore();
  },
};

/**
 * Execute the CLI command passed in process.argv[2].
 * @param argv Arguments vector.
 */
export function runCli(argv: string[] = process.argv): void {
  const verb = argv[2];
  const command = verb ? commands[verb] : undefined;

  if (!command) {
    const usage = Object.keys(commands)
      .map(name => `  commons-expo ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void command();
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli();
}
