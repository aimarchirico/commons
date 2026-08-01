import {coverageConfigDefaults, defineConfig} from 'vitest/config';

/**
 * Shared coverage configuration enforcing an 80% floor on lines, functions,
 * branches, and statements.
 */
export const vitestCoverageConfig = defineConfig({
  test: {
    coverage: {
      enabled: true,
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
      exclude: [
        ...coverageConfigDefaults.exclude,
        '**/bin/**',
        '**/assets/**',
        '**/eslint-base.ts',
        '**/eslint-core.ts',
        '**/vitest-coverage.ts',
      ],
    },
  },
});

export default vitestCoverageConfig;
