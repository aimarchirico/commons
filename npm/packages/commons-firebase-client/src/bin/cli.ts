#!/usr/bin/env node

const commands: Record<string, string> = {
  'decode-google-services': './decode-google-services.js',
};

const verb = process.argv[2];
const script = verb ? commands[verb] : undefined;

if (!script) {
  const usage = Object.keys(commands)
    .map(name => `  commons-firebase-client ${name}`)
    .join('\n');
  console.error(`Usage:\n${usage}`);
  process.exit(1);
}

void import(script);
