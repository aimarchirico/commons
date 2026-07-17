export default {
  config: {
    default: true,
    MD013: {code_blocks: false, tables: false},
  },
  globs: ['**/*.md'],
  ignores: [
    '**/node_modules/**',
    '**/dist/**',
    '**/build/**',
    '**/target/**',
    '**/CHANGELOG.md',
  ],
  overrides: [
    {
      filter: ['**/SKILL.md', '**/PULL_REQUEST_TEMPLATE.md'],
      config: {
        MD041: false,
      },
      combine: 'merge',
    },
  ],
};
