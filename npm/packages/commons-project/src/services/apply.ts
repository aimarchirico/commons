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

/**
 * Derive the literal pairs a rule replaces. Longer literals go first so a
 * shorter variant cannot corrupt a longer one that contains it.
 */
const pairs = (
  replacement: ManifestReplacement,
  manifest: Manifest,
): Pair[] => {
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
};

export const applyReplacement = async (
  replacement: ManifestReplacement,
  manifest: Manifest,
): Promise<number> => {
  const replacements = pairs(replacement, manifest);
  if (!replacements.length) return 0;

  const files = await glob(replacement.files, {ignore: IGNORE, dot: true});
  let changed = 0;

  for (const file of files) {
    const original = fs.readFileSync(file, 'utf8');
    let content = original;
    for (const pair of replacements) {
      content = content.split(pair.from).join(pair.to);
    }
    if (content !== original) {
      fs.writeFileSync(file, content);
      changed += 1;
    }
  }

  return changed;
};

const pruneEmptyParents = (from: string, stopAt: string): void => {
  let parent = path.dirname(path.resolve(from));
  const root = path.resolve(stopAt);
  while (parent.startsWith(root) && parent !== root) {
    if (fs.readdirSync(parent).length) return;
    fs.rmdirSync(parent);
    parent = path.dirname(parent);
  }
};

export const applyMove = (
  move: ManifestMove,
  manifest: Manifest,
): {moved: boolean; from: string; to: string} => {
  const from = interpolate(move.from, 'from', manifest.values);
  const to = interpolate(move.to, 'to', manifest.values);
  const unchanged = {moved: false, from, to};

  if (path.resolve(from) === path.resolve(to)) return unchanged;
  if (!fs.existsSync(from)) return unchanged;

  const parent = path.dirname(to);
  if (parent) fs.mkdirSync(parent, {recursive: true});
  if (fs.existsSync(to)) fs.rmSync(to, {recursive: true, force: true});
  fs.renameSync(from, to);
  pruneEmptyParents(from, process.cwd());
  return {moved: true, from, to};
};

export const applyDelete = (target: string): 'deleted' | 'skipped' => {
  if (!fs.existsSync(target)) return 'skipped';
  fs.rmSync(target, {recursive: true, force: true});
  return 'deleted';
};
