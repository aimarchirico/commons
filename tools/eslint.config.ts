let tsConfig;
let toolsConfig;

try {
  tsConfig = (await import('@aimarchirico/commons-ts/eslint')).default;
  toolsConfig = (await import('@aimarchirico/commons-tools/eslint')).default;
} catch {
  tsConfig = (await import('../npm/packages/commons-ts/eslint.ts')).default;
  toolsConfig = (await import('../npm/packages/commons-tools/eslint.ts'))
    .default;
}

export default [
  ...tsConfig,
  ...toolsConfig,
  {
    ignores: [
      '../npm/packages/**/*',
      '../**/.turbo/**',
      '../**/pnpm-lock.yaml',
      '../**/commitlint.config.js',
    ],
  },
  {
    files: ['**/eslint.config.ts'],
    rules: {
      'import/no-default-export': 'off',
      'check-file/filename-naming-convention': 'off',
    },
  },
];
