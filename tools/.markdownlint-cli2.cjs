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
  ],
   overrides: [
      {
        filter: ['../**/SKILL.md', '../**/PULL_REQUEST_TEMPLATE.md'],
        config: {
          "MD041": false
        },
        combine: 'merge'
      }
    ]
};
