#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {applyDelete, applyMove, applyReplacement} from '../services/apply.js';
import {loadManifest, manifestPath} from '../services/manifest.js';

async function run(): Promise<void> {
  const env = resolveEnv([], ['PROJECT_ROOT']);
  const root = env.PROJECT_ROOT || process.cwd();
  const manifest = loadManifest();
  console.log(`Applying ${manifestPath()}\n`);

  for (const replacement of manifest.replacements ?? []) {
    const changed = await applyReplacement(replacement, manifest, root);
    report(
      `replace ${replacement.value}`,
      changed ? 'updated' : 'present',
      changed ? `${changed} file(s)` : 'no occurrences left',
    );
  }

  for (const move of manifest.moves ?? []) {
    const {moved, from, to} = applyMove(move, manifest, root);
    report(
      `move ${from}`,
      moved ? 'updated' : 'present',
      moved ? `to ${to}` : 'source absent',
    );
  }

  for (const target of manifest.deletes ?? []) {
    const outcome = applyDelete(target, root);
    report(`delete ${target}`, outcome === 'deleted' ? 'updated' : 'present');
  }

  printSummary('commons-project rename-project');
}

run().catch((error: unknown) => {
  fail(error instanceof Error ? error.message : String(error));
});
