import fs from 'fs';

const SECRET_HINT = /(SECRET|PASSWORD|TOKEN|KEY|BASE64)/;

const mask = (name: string, value: string): string =>
  SECRET_HINT.test(name) ? `<${value.length} characters>` : value;

/**
 * Emit values a caller needs to chain onward. When `OUTPUT_FILE` is set the
 * values are appended to it as `KEY=value` lines so a shell can source them;
 * otherwise they are printed with sensitive values masked.
 * @param values
 */
export const writeOutputs = (values: Record<string, string>): void => {
  const target = process.env.OUTPUT_FILE;
  const names = Object.keys(values);
  if (!names.length) return;

  if (target) {
    const lines = names.map(name => `${name}=${values[name]}\n`).join('');
    fs.appendFileSync(target, lines, {mode: 0o600});
    console.log(`  outputs written to ${target}: ${names.join(', ')}`);
    return;
  }

  for (const name of names) {
    console.log(`  ${name}=${mask(name, values[name])}`);
  }
};
