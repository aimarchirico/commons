import expoConfig from 'eslint-config-expo/flat.js';
import baseConfig from '@aimarchirico/commons-eslint';

const dedupedConfig = baseConfig.map(config => {
  if (!config?.plugins) return config;
  const { '@typescript-eslint': _tsPlugin, import: _importPlugin, ...plugins } = config.plugins;
  return {...config, plugins};
});

export default baseConfig;
