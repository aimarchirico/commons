import baseConfig from './src/lib/eslint-core';

const config = [
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];

export default config;
