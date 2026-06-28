const baseConfig = require('@aimarchirico/core-docs/markdownlint');

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
