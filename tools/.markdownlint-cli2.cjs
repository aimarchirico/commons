module.exports = {
  config: {
    default: true,
    MD013: { code_blocks: false, tables: false },
  },
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
