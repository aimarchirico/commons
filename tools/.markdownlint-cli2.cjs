const baseConfig = require('@aimarchirico/commons-tools/markdownlint');

module.exports = {
  ...baseConfig,
  gitignore: false,
  globs: ['../**/*.md'],
  ignores: [
    '../**/node_modules/**',
    '../**/dist/**',
    '../**/build/**',
    '../**/target/**',
    '../**/CHANGELOG.md',
  ],
};
