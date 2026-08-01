import baseConfig from '@aimarchirico/commons-ts/eslint-core';

const config = [
  ...baseConfig,
  {
    files: ['**/eslint*.ts', '**/vitest-coverage.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];

export default config;
