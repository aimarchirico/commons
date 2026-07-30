/** The result of acting on a single provisioning resource. */
export type Outcome =
  'created' | 'updated' | 'present' | 'written' | 'skipped' | 'pending';

type Entry = {resource: string; outcome: Outcome; detail?: string};

type Instruction = {resource: string; steps: string[]};

const MARKS: Record<Outcome, string> = {
  created: '+',
  updated: '~',
  present: '=',
  written: '*',
  skipped: '-',
  pending: '!',
};

const LABELS: Record<Outcome, string> = {
  created: 'created',
  updated: 'updated',
  present: 'already present',
  written: 'written',
  skipped: 'skipped',
  pending: 'action required',
};

const entries: Entry[] = [];
const instructions: Instruction[] = [];

/**
 * Report the outcome of a provisioning resource.
 * @param resource The name of the resource.
 * @param outcome The outcome of the action.
 * @param detail Optional detail string.
 */
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
 * Print how a value the command is about to act on was resolved. A derived
 * value that is wrong is otherwise indistinguishable from a supplied one, and
 * the consequences — writing to the wrong repository, say — are not reversible
 * by re-running.
 * @param label
 * @param value
 * @param source
 */
export const context = (label: string, value: string, source: string): void => {
  console.log(`· ${label} ${value} (${source})`);
};

/**
 * Record a step only a human can take. It reports like any other outcome so a
 * run reads consistently, and repeats in full at the end of the summary so it
 * cannot be lost in the middle of the output. Distinct from a failure: the
 * command did everything it could, and the rest is waiting on someone.
 * @param resource
 * @param detail
 * @param steps
 */
export const instruct = (
  resource: string,
  detail: string,
  steps: string[],
): void => {
  instructions.push({resource, steps});
  report(resource, 'pending', detail);
};

/**
 * Wrap a provisioning step so its outcome is reported consistently and an
 * unexpected failure names the resource it was working on.
 * @param resource
 * @param action
 * @returns The resolved value of type T, or undefined.
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
 * @param title
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
  const settled = !changed && !instructions.length;
  console.log(
    `\n${title}: ${parts.length ? parts.join(', ') : 'nothing to do'}${
      settled ? ' — no changes' : ''
    }`,
  );

  for (const instruction of instructions) {
    console.log(`\nAction required — ${instruction.resource}:`);
    for (const line of instruction.steps) {
      console.log(`  ${line}`);
    }
  }
};

/**
 * Annotated rather than inferred so callers get control-flow narrowing after a
 * `fail(...)` call.
 * @param message The error message.
 * @returns Never returns as it exits the process.
 */
export const fail: (message: string) => never = message => {
  console.error(message);
  process.exit(1);
};
