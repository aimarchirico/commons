#!/usr/bin/env node

import {pathToFileURL} from 'url';

const commands: Record<string, string> = {
  'build-android': './build-android.js',
  'create-project': './create-project.js',
  'import-keystore': './import-keystore.js',
};

/**
 * Execute the CLI command passed in process.argv[2].
 * @param argv Arguments vector.
 */
export function runCli(argv: string[] = process.argv): void {
  const verb = argv[2];
  const script = verb ? commands[verb] : undefined;

  if (!script) {
    const usage = Object.keys(commands)
      .map(name => `  commons-expo ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void import(script);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli();
}
