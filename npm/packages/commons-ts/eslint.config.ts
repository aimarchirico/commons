import baseConfig from '@aimarchirico/commons-ts/eslint';
export default [
  ...baseConfig,
  {
    files: ['**/eslint.ts'],
    rules: {
      'check-file/filename-naming-convention': 'off',
      'import/no-default-export': 'off',
    },
  },
];
