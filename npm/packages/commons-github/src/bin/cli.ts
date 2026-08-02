#!/usr/bin/env node

import {pathToFileURL} from 'url';

const commands: Record<string, string> = {
  'create-project': './create-project.js',
  'create-environments': './create-environments.js',
  'sync-variables': './sync-variables.js',
  'set-secrets': './set-secrets.js',
  'materialize-templates': './materialize-templates.js',
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
      .map(name => `  commons-github ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void import(script);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli();
}
