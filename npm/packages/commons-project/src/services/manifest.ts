import fs from 'fs';
import path from 'path';
import {isTransform, transform} from './transforms.js';
import type {Manifest, ManifestValue} from '../types/manifest.js';

const PLACEHOLDER =
  /\{\{\s*([A-Za-z0-9_]+)(?:\.(from|to))?(?:\|([A-Za-z]+))?\s*\}\}/g;

/** Which half of a manifest value a placeholder or field reads from. */
export type Side = 'from' | 'to';

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const isStringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every(entry => typeof entry === 'string');

/**
 * Resolve `{{value}}`, `{{value|transform}}`, and `{{value.from|transform}}`
 * against the manifest's values. Unqualified placeholders take the side of the
 * field they appear in, so a move's `from` reads source values and its `to`
 * reads target values.
 * @param template
 * @param side
 * @param values
 * @returns The interpolated string.
 */
export const interpolate = (
  template: string,
  side: Side,
  values: Record<string, ManifestValue>,
): string =>
  template.replace(PLACEHOLDER, (_match, name, explicit, transformName) => {
    const value = values[name];
    if (!value) throw new Error(`Unknown manifest value "${name}".`);
    const raw = value[(explicit as Side) ?? side];
    return transformName ? transform(transformName, raw) : raw;
  });

const validatePlaceholders = (
  template: string,
  values: Record<string, ManifestValue>,
  where: string,
  errors: string[],
): void => {
  for (const match of template.matchAll(PLACEHOLDER)) {
    const [, name, , transformName] = match;
    if (!(name in values)) {
      errors.push(`${where}: unknown manifest value "${name}".`);
    }
    if (transformName && !isTransform(transformName)) {
      errors.push(`${where}: unknown transform "${transformName}".`);
    }
  }
};

const validate = (data: unknown): Manifest => {
  const errors: string[] = [];

  if (!isRecord(data)) {
    throw new Error('Manifest must be a JSON object.');
  }

  const values: Record<string, ManifestValue> = {};
  if (!isRecord(data.values)) {
    errors.push('"values" must be an object of {from, to} pairs.');
  } else {
    for (const [name, entry] of Object.entries(data.values)) {
      if (
        !isRecord(entry) ||
        typeof entry.from !== 'string' ||
        typeof entry.to !== 'string' ||
        !entry.from
      ) {
        errors.push(
          `values.${name}: must be {"from": "<non-empty>", "to": "<string>"}.`,
        );
        continue;
      }
      values[name] = {from: entry.from, to: entry.to};
    }
  }

  const replacements = data.replacements ?? [];
  if (!Array.isArray(replacements)) {
    errors.push('"replacements" must be an array.');
  } else {
    replacements.forEach((entry, index) => {
      const where = `replacements[${index}]`;
      if (!isRecord(entry)) {
        errors.push(`${where}: must be an object.`);
        return;
      }
      if (typeof entry.value !== 'string' || !(entry.value in values)) {
        errors.push(`${where}.value: unknown manifest value "${entry.value}".`);
      }
      if (!isStringArray(entry.files) || !entry.files.length) {
        errors.push(`${where}.files: must be a non-empty array of globs.`);
      }
      if (entry.transforms !== undefined && !isStringArray(entry.transforms)) {
        errors.push(
          `${where}.transforms: must be an array of transform names.`,
        );
      } else {
        for (const name of (entry.transforms as string[] | undefined) ?? []) {
          if (!isTransform(name)) {
            errors.push(`${where}.transforms: unknown transform "${name}".`);
          }
        }
      }
    });
  }

  const moves = data.moves ?? [];
  if (!Array.isArray(moves)) {
    errors.push('"moves" must be an array.');
  } else {
    moves.forEach((entry, index) => {
      const where = `moves[${index}]`;
      if (
        !isRecord(entry) ||
        typeof entry.from !== 'string' ||
        typeof entry.to !== 'string'
      ) {
        errors.push(`${where}: must be {"from": "<path>", "to": "<path>"}.`);
        return;
      }
      validatePlaceholders(entry.from, values, `${where}.from`, errors);
      validatePlaceholders(entry.to, values, `${where}.to`, errors);
    });
  }

  const deletes = data.deletes ?? [];
  if (!isStringArray(deletes)) {
    errors.push('"deletes" must be an array of paths.');
  }

  if (errors.length) {
    throw new Error(
      `Manifest is unusable, nothing was applied:\n${errors
        .map(message => `  - ${message}`)
        .join('\n')}`,
    );
  }

  return {
    values,
    replacements: replacements as Manifest['replacements'],
    moves: moves as Manifest['moves'],
    deletes: deletes as string[],
  };
};

/**
 * Resolve the manifest path from `MANIFEST_PATH`, defaulting to
 * `manifest.json` in the working directory.
 * @returns The resolved manifest file path.
 */
export const manifestPath = (): string =>
  path.resolve(process.env.MANIFEST_PATH ?? 'manifest.json');

/**
 * Load and validate the manifest.
 * @returns The loaded and validated Manifest object.
 */
export const loadManifest = (): Manifest => {
  const file = manifestPath();
  if (!fs.existsSync(file)) {
    throw new Error(
      `No manifest at ${file}. Set MANIFEST_PATH to the manifest describing the rename.`,
    );
  }
  let data: unknown;
  try {
    data = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Manifest at ${file} is not valid JSON: ${message}`);
  }
  return validate(data);
};
