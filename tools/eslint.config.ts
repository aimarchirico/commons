let tsConfig;
let jsonConfig;
let ymlConfig;
let tomlConfig;

try {
  tsConfig = (await import('@aimarchirico/commons-eslint')).default;
} catch {
  tsConfig = (await import('../npm/packages/commons-eslint/index.js')).default;
}

export default [
  ...tsConfig,
  {
    ignores: [
      '../npm/packages/**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}',
      '../**/.turbo/**',
      '**/pnpm-lock.yaml',
      '../**/pnpm-lock.yaml',
      '**/commitlint.config.js',
      '../**/commitlint.config.js',
      '**/test.toml',
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
