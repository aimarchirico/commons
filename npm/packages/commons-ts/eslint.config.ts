import baseConfig from '@aimarchirico/commons-ts/eslint-core';
export default [
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];
