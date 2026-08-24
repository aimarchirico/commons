const commands: Record<string, () => Promise<void>> = {
  'sync-env': async () => {
    const {syncEnv} = await import('./sync-env.js');
    syncEnv();
  },
  'copy-files': async () => {
    const {copyFiles} = await import('./copy-files.js');
    copyFiles();
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
      .map(name => `  commons-ssh ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void command();
}
