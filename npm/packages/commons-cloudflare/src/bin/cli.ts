#!/usr/bin/env node

import {pathToFileURL} from 'url';

const commands: Record<string, () => Promise<void>> = {
  'fix-assets': async () => {
    const {fixAssets} = await import('./fix-assets.js');
    fixAssets();
  },
  'create-pages-project': async () => {
    const {createPagesProject} = await import('./create-pages-project.js');
    await createPagesProject();
  },
  'set-pages-env': async () => {
    const {setPagesEnv} = await import('./set-pages-env.js');
    await setPagesEnv();
  },
  'add-tunnel-route': async () => {
    const {addTunnelRoute} = await import('./add-tunnel-route.js');
    await addTunnelRoute();
  },
  'create-service-token': async () => {
    const {createServiceToken} = await import('./create-service-token.js');
    await createServiceToken();
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
      .map(name => `  commons-cloudflare ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void command();
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli();
}
