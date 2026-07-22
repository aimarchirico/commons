import baseConfig from '@aimarchirico/commons-ts/eslint';
export default [
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];
