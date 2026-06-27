import coreConfig from "@aimarchirico/core-eslint";

export default [
  ...coreConfig,
  {
    ignores: [
      "**/node_modules/**",
      "**/build/**",
      "**/dist/**",
      "**/.gradle/**"
    ]
  }
];
