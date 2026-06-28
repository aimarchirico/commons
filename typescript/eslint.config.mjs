import globals from 'globals';
import coreConfig from '@aimarchirico/core-eslint';

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/build/**',
      '**/dist/**',
      '**/.gradle/**',
      '**/.idea/**',
      '**/.vscode/**',
      '**/out/**'
    ]
  },
  ...coreConfig,
  {
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.commonjs
      }
    },
    rules: {
      'prettier/prettier': 'off',
      'quotes': ['warn', 'single']
    }
  }
];
