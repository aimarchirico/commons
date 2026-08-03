#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveTool,
  runJson,
  writeOutputs,
} from '@aimarchirico/commons-project';

type Initialized = {
  status: string;
  projectId: string;
  owner: string;
  slug: string;
  dashboardUrl: string;
};

/**
 * Create or link an EAS project for the current Expo app.
 */
export function createProject(): void {
  const eas = resolveTool({
    from: import.meta.url,
    package: 'eas-cli',
    bin: 'eas',
    minVersion: '21.0.0',
    installHint:
      'Add it to the project with "pnpm add -D eas-cli", then authenticate with "pnpm exec eas login" or set EXPO_TOKEN.',
  });

  const args = ['init', '--non-interactive', '--json', '--force'];

  try {
    const result = runJson<Initialized>(eas, args);
    report(
      `eas project ${result.owner}/${result.slug}`,
      result.status === 'created' ? 'created' : 'present',
      result.projectId,
    );
    writeOutputs({EAS_PROJECT_ID: result.projectId});
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  printSummary('create-project');
}
