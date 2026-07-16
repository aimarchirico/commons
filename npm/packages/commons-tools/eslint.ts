import eslintPluginYml from 'eslint-plugin-yml';
import eslintPluginToml from 'eslint-plugin-toml';

export default [
  ...eslintPluginYml.configs['flat/recommended'],
  ...eslintPluginToml.configs['flat/recommended'],
];
