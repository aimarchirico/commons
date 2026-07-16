// @ts-nocheck
import expoConfig from 'eslint-config-expo/flat.js';
import baseConfig from './index.js';

const dedupedConfig = baseConfig.map(config => {
  if (!config?.plugins) {
    return config;
  }
  const {
    '@typescript-eslint': _tsPlugin,
    import: _importPlugin,
    ...plugins
  } = config.plugins;
  return {...config, plugins};
});

export default [...expoConfig, ...dedupedConfig];
