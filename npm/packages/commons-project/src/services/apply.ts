import fs from 'fs';
import path from 'path';
import {glob} from 'tinyglobby';
import {interpolate} from './manifest.js';
import {transform} from './transforms.js';
import type {
  Manifest,
  ManifestMove,
  ManifestReplacement,
} from '../types/manifest.js';

const IGNORE = [
  '**/node_modules/**',
  '**/.git/**',
  '**/build/**',
  '**/dist/**',
  '**/.gradle/**',
];

type Pair = {from: string; to: string};

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function boundaryPattern(from: string): RegExp {
  return new RegExp(
    `(?<![A-Za-z0-9_-])${escapeRegExp(from)}(?![A-Za-z0-9_-])`,
    'g',
  );
}

function pairs(replacement: ManifestReplacement, manifest: Manifest): Pair[] {
  const value = manifest.values[replacement.value];
  const names = replacement.transforms?.length
    ? replacement.transforms
    : ['identity'];
  const seen = new Set<string>();
  return names
    .map(name => ({
      from: transform(name, value.from),
      to: transform(name, value.to),
    }))
    .filter(pair => {
      if (pair.from === pair.to || seen.has(pair.from)) return false;
      seen.add(pair.from);
      return true;
    })
    .sort((a, b) => b.from.length - a.from.length);
}

/**
 * Apply a replacement rule to the matched files.
 * @param replacement The replacement config.
 * @param manifest The project manifest.
 * @param root Directory the replacement's file patterns resolve against.
 *   Defaults to the current working directory.
 * @returns The number of files changed.
 */
export async function applyReplacement(
  replacement: ManifestReplacement,
  manifest: Manifest,
  root: string = process.cwd(),
): Promise<number> {
  const replacements = pairs(replacement, manifest);
  if (!replacements.length) return 0;

  const files = await glob(replacement.files, {
    cwd: root,
    ignore: IGNORE,
    dot: true,
    absolute: true,
  });
  let changed = 0;

  for (const file of files) {
    const original = fs.readFileSync(file, 'utf8');
    let content = original;
    for (const pair of replacements) {
      content = content.replace(boundaryPattern(pair.from), pair.to);
    }
    if (content !== original) {
      fs.writeFileSync(file, content);
      changed += 1;
    }
  }

  return changed;
}

function pruneEmptyParents(from: string, stopAt: string): void {
  let parent = path.dirname(path.resolve(from));
  const root = path.resolve(stopAt);
  while (parent.startsWith(root) && parent !== root) {
    if (fs.readdirSync(parent).length) return;
    fs.rmdirSync(parent);
    parent = path.dirname(parent);
  }
}

/**
 * Move a file or directory.
 * @param move The move instruction config.
 * @param manifest The project manifest.
 * @param root Directory from/to resolve against. Defaults to the current
 *   working directory.
 * @returns The status and final paths, reported relative to `root`.
 */
export function applyMove(
  move: ManifestMove,
  manifest: Manifest,
  root: string = process.cwd(),
): {moved: boolean; from: string; to: string} {
  const from = interpolate(move.from, 'from', manifest.values);
  const to = interpolate(move.to, 'to', manifest.values);
  const unchanged = {moved: false, from, to};

  const fromPath = path.join(root, from);
  const toPath = path.join(root, to);
  if (path.resolve(fromPath) === path.resolve(toPath)) return unchanged;
  if (!fs.existsSync(fromPath)) return unchanged;

  const parent = path.dirname(toPath);
  if (parent) fs.mkdirSync(parent, {recursive: true});
  if (fs.existsSync(toPath)) fs.rmSync(toPath, {recursive: true, force: true});
  fs.renameSync(fromPath, toPath);
  pruneEmptyParents(fromPath, root);
  return {moved: true, from, to};
}

/**
 * Delete a file or directory.
 * @param target The target path to delete.
 * @param root Directory target resolves against. Defaults to the current
 *   working directory.
 * @returns The outcome status.
 */
export function applyDelete(
  target: string,
  root: string = process.cwd(),
): 'deleted' | 'skipped' {
  const targetPath = path.join(root, target);
  if (!fs.existsSync(targetPath)) return 'skipped';
  fs.rmSync(targetPath, {recursive: true, force: true});
  return 'deleted';
}
