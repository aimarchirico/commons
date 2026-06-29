module.exports = {
  config: {
    default: true,
    MD013: false,
    MD033: false,
    MD041: false,
    MD024: {
      siblings_only: true
    }
  },
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
