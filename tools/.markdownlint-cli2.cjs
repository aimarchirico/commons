const baseConfig = require('@aimarchirico/commons-tools/markdownlint');

module.exports = {
  ...baseConfig,
  globs: ['../**/*.md'],
  ignores: [
    '../**/node_modules/**',
    '../**/dist/**',
    '../**/build/**',
    '../**/target/**',
    '../**/CHANGELOG.md',
    '../**/SKILL.md',
    '../**/PULL_REQUEST_TEMPLATE.md',
  ],
};
