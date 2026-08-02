import {defineConfig, mergeConfig} from 'vitest/config';
import base from '@aimarchirico/commons-ts/vitest-base';

/** Vitest configuration. */
export default mergeConfig(
  base,
  defineConfig({
    test: {
      environment: 'jsdom',
    },
  }),
);
