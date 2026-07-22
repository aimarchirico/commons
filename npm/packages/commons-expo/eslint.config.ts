import baseConfig from '@aimarchirico/commons-expo/eslint';
export default [
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];
