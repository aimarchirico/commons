import coreConfig from "@aimarchirico/core-ts/eslint";

export default [
  {
    ignores: [
      'node_modules/**',
      'packages/core-ts/eslint.config.mjs',
      'packages/core-ts/bin/cli.js',
      'packages/core-docs/bin/cli.js',
      'packages/core-tools/.markdownlint-cli2.cjs',
      'packages/core-tools/commitlint.cjs',
      'packages/core-api/bin/cli.js',
      'eslint.config.mjs'
    ],
  },
  ...coreConfig,
];
