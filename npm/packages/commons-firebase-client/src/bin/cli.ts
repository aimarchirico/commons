const commands: Record<string, () => Promise<void>> = {
  'decode-google-services': async () => {
    const {decodeGoogleServices} = await import('./decode-google-services.js');
    decodeGoogleServices();
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
      .map(name => `  commons-firebase-client ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void command();
}
