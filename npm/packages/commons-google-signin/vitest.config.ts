import base from '@aimarchirico/commons-ts/vitest-coverage';

/**
 * Extends the shared coverage config with `hooks/` and `contexts/`, which
 * hold React hooks/context that would need `@testing-library/react` and a
 * DOM environment to test meaningfully. That setup is disproportionate for
 * this package's size, so they are treated like `bin/`: thin glue excluded
 * from the threshold, with `services/` carrying the coverage bar instead.
 */
export default {
  ...base,
  test: {
    ...base.test,
    coverage: {
      ...base.test?.coverage,
      exclude: [
        ...(base.test?.coverage?.exclude ?? []),
        '**/hooks/**',
        '**/contexts/**',
      ],
    },
  },
};
