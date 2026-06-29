module.exports = {
  config: {
    default: true,
    MD013: false,
    MD033: false,
    MD041: false,
    MD024: {
      siblings_only: true,
    },
  },
  globs: ['**/*.md'],
  ignores: ['**/CHANGELOG.md'],
  gitignore: true,
};
