import {defineConfig} from 'vitest/config';
import base from '@aimarchirico/commons-ts/vitest-base';

/** Vitest configuration. */
export default defineConfig({
  ...base,
  test: {
    ...base.test,
    environment: 'jsdom',
  },
});
