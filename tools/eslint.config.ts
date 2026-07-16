let baseConfig;
try {
  baseConfig = (await import('@aimarchirico/commons-ts/eslint')).default;
} catch {
  baseConfig = (await import('../npm/packages/commons-ts/eslint.ts')).default;
}

export default [
  ...baseConfig,
  {
    ignores: [
      '../npm/packages/**/*',
      '../npm/apps/**/*',
      '../backend/**/*',
      '../frontend/**/*',
      '../**/pnpm-lock.yaml'
    ],
  },
];
