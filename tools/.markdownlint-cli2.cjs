const baseConfig = require('@aimarchirico/core-tools/markdownlint');

module.exports = {
  ...baseConfig,
  globs: [
    "../**/*.md"
  ],
  ignores: [
    "../**/node_modules/**",
    "../**/dist/**",
    "../**/.expo/**",
    "../**/.git/**",
    "../maven/**/build/**",
    "../maven/**/.gradle/**",
    "../**/tmp/**",
    "node_modules/**",
    ".turbo/**"
  ]
};
