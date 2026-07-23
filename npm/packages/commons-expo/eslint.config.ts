import baseConfig from './src/lib/eslint-base';
export default [
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];
