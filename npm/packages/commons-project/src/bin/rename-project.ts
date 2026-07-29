#!/usr/bin/env node

import {fail, printSummary, report} from '@aimarchirico/commons-project';
import {applyDelete, applyMove, applyReplacement} from '../services/apply.js';
import {loadManifest, manifestPath} from '../services/manifest.js';

const run = async (): Promise<void> => {
  const manifest = loadManifest();
  console.log(`Applying ${manifestPath()}\n`);

  for (const replacement of manifest.replacements ?? []) {
    const changed = await applyReplacement(replacement, manifest);
    report(
      `replace ${replacement.value}`,
      changed ? 'updated' : 'present',
      changed ? `${changed} file(s)` : 'no occurrences left',
    );
  }

  for (const move of manifest.moves ?? []) {
    const {moved, from, to} = applyMove(move, manifest);
    report(
      `move ${from}`,
      moved ? 'updated' : 'present',
      moved ? `to ${to}` : 'source absent',
    );
  }

  for (const target of manifest.deletes ?? []) {
    const outcome = applyDelete(target);
    report(`delete ${target}`, outcome === 'deleted' ? 'updated' : 'present');
  }

  printSummary('rename-project');
};

run().catch((error: unknown) => {
  fail(error instanceof Error ? error.message : String(error));
});
