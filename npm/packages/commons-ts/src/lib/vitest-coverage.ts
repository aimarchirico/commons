import {coverageConfigDefaults, defineConfig} from 'vitest/config';

/**
 * Shared coverage configuration enforcing an 80% floor on lines, functions,
 * branches, and statements. Consumers import and re-export this from their
 * own `vitest.config.ts` with zero additional config.
 *
 * Published as compiled JS (`dist/lib/vitest-coverage.js`, built via
 * `tsconfig.build.json`), not raw `.ts`: Vite's config loader bundles a
 * `vitest.config.ts`'s own relative imports, but externalizes bare-specifier
 * imports resolved into `node_modules` (including pnpm workspace symlinks)
 * and hands them to Node's native loader, which cannot import raw
 * TypeScript.
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
