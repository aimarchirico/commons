module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Aligned with the commit-type table in CONTRIBUTING.md ("## Commits").
    'type-enum': [
      2,
      'always',
      [
        'fix',
        'feat',
        'build',
        'chore',
        'ci',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'revert',
      ],
    ],
  },
};
