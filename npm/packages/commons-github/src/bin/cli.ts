const commands: Record<string, () => Promise<void>> = {
  'create-project': async () => {
    const {createProject} = await import('./create-project.js');
    createProject();
  },
  'create-environments': async () => {
    const {createEnvironments} = await import('./create-environments.js');
    createEnvironments();
  },
  'sync-variables': async () => {
    const {syncVariables} = await import('./sync-variables.js');
    syncVariables();
  },
  'set-secrets': async () => {
    const {setSecrets} = await import('./set-secrets.js');
    setSecrets();
  },
  'materialize-templates': async () => {
    const {materializeTemplates} = await import('./materialize-templates.js');
    materializeTemplates();
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
      .map(name => `  commons-github ${name}`)
      .join('\n');
    console.error(`Usage:\n${usage}`);
    process.exit(1);
  }

  void command();
}
