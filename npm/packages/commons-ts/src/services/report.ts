export type Outcome = 'created' | 'updated' | 'present' | 'written' | 'skipped';

type Entry = {resource: string; outcome: Outcome; detail?: string};

const MARKS: Record<Outcome, string> = {
  created: '+',
  updated: '~',
  present: '=',
  written: '*',
  skipped: '-',
};

const LABELS: Record<Outcome, string> = {
  created: 'created',
  updated: 'updated',
  present: 'already present',
  written: 'written',
  skipped: 'skipped',
};

const entries: Entry[] = [];

export const report = (
  resource: string,
  outcome: Outcome,
  detail?: string,
): void => {
  entries.push({resource, outcome, detail});
  const suffix = detail ? ` (${detail})` : '';
  console.log(`${MARKS[outcome]} ${resource}: ${LABELS[outcome]}${suffix}`);
};

/**
 * Wrap a provisioning step so its outcome is reported consistently and an
 * unexpected failure names the resource it was working on.
 */
export const step = async <T>(
  resource: string,
  action: () => Promise<{outcome: Outcome; detail?: string; value?: T}>,
): Promise<T | undefined> => {
  try {
    const result = await action();
    report(resource, result.outcome, result.detail);
    return result.value;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`! ${resource}: failed\n  ${message}`);
    process.exit(1);
  }
};

/**
 * Print a one-line tally so a re-run reads at a glance as a run in which
 * nothing changed.
 */
export const printSummary = (title: string): void => {
  const counts = entries.reduce<Record<string, number>>((acc, entry) => {
    acc[entry.outcome] = (acc[entry.outcome] ?? 0) + 1;
    return acc;
  }, {});
  const parts = (Object.keys(MARKS) as Outcome[])
    .filter(outcome => counts[outcome])
    .map(outcome => `${counts[outcome]} ${LABELS[outcome]}`);
  const changed = entries.some(
    entry => entry.outcome === 'created' || entry.outcome === 'updated',
  );
  console.log(
    `\n${title}: ${parts.length ? parts.join(', ') : 'nothing to do'}${
      changed ? '' : ' — no changes'
    }`,
  );
};

export const fail = (message: string): never => {
  console.error(message);
  process.exit(1);
};
