const baseConfig = require('@aimarchirico/core-markdown/.markdownlint-cli2.cjs');

module.exports = {
  ...baseConfig,
  ignores: [
    '**/node_modules/**',
    '**/build/**',
    '**/dist/**',
    '**/.gradle/**',
    '**/.git/**',
    '**/tmp/**'
  ]
};
