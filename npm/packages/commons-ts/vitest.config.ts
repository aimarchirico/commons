import {defineConfig} from 'vitest/config';
import base from './src/lib/vitest-coverage';

/**
 * Extends the shared coverage config with this package's own `eslint-base.ts`
 * and `eslint-core.ts`, which are declarative rule-set exports rather than
 * logic worth unit testing.
 */
export default defineConfig({
  ...base,
  test: {
    ...base.test,
    coverage: {
      ...base.test?.coverage,
      exclude: [
        ...(base.test?.coverage?.exclude ?? []),
        '**/eslint-base.ts',
        '**/eslint-core.ts',
      ],
    },
  },
});
