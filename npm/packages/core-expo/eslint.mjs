import {defineConfig} from 'eslint/config';
import expoConfig from 'eslint-config-expo/flat.js';
import baseConfig from '@aimarchirico/core-ts/eslint';

const dedupedBaseConfig = baseConfig.map(config => {
  if (!config?.plugins?.import) {
    return config;
  }
  const {import: _importPlugin, ...plugins} = config.plugins;
  return {...config, plugins};
});

export default defineConfig([...expoConfig, ...dedupedBaseConfig]);
