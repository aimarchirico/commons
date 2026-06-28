import coreConfig from "@aimarchirico/core-eslint";

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/build/**',
      '**/dist/**',
      '**/.gradle/**',
      '**/.idea/**',
      '**/.vscode/**',
      '**/out/**',
      'packages/core-docs/scripts/materialize.js',
      'packages/core-openapi/scripts/generate-api.js',
      'packages/core-markdown/.markdownlint-cli2.cjs',
      'packages/core-eslint/eslint.config.mjs',
      'eslint.config.mjs'
    ],
  },
  ...coreConfig,
];
