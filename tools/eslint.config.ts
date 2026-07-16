let tsConfig;
let jsonConfig;
let ymlConfig;
let tomlConfig;

try {
  tsConfig = (await import('@aimarchirico/commons-eslint')).default;
  jsonConfig = (await import('@aimarchirico/commons-eslint/json')).default;
  ymlConfig = (await import('@aimarchirico/commons-eslint/yaml')).default;
  tomlConfig = (await import('@aimarchirico/commons-eslint/toml')).default;
} catch {
  tsConfig = (await import('../npm/packages/commons-eslint/index.js')).default;
  jsonConfig = (await import('../npm/packages/commons-eslint/json.js')).default;
  ymlConfig = (await import('../npm/packages/commons-eslint/yaml.js')).default;
  tomlConfig = (await import('../npm/packages/commons-eslint/toml.js')).default;
}

export default [
  ...tsConfig,
  ...jsonConfig,
  ...ymlConfig,
  ...tomlConfig,
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
