import baseConfig from './src/lib/eslint-core';
export default [
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];
