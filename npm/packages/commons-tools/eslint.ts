// @ts-ignore
import eslintPluginJsonc from 'eslint-plugin-jsonc';
// @ts-ignore
import eslintPluginYml from 'eslint-plugin-yml';

export default [
  ...eslintPluginJsonc.configs['flat/recommended-with-jsonc'],
  ...eslintPluginYml.configs['flat/recommended'],
  {
    files: ['**/*.{yml,yaml}'],
    rules: {}
  },
  {
    files: ['**/*.{json,jsonc,json5}'],
    rules: {}
  }
];
