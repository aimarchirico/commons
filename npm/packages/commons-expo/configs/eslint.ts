import type {Linter} from 'eslint';
import baseConfig from '@aimarchirico/commons-ts/eslint';
import {expoConfig} from './eslint-config-expo';

const flatExpo = expoConfig.flat(Infinity) as Linter.Config[];
const primaryTsPlugin = flatExpo.find(c => c.plugins?.['@typescript-eslint'])
  ?.plugins?.['@typescript-eslint'];
const primaryImportPlugin = flatExpo.find(c => c.plugins?.['import'])
  ?.plugins?.['import'];

const combined = (
  [...expoConfig, ...baseConfig].flat(Infinity) as Linter.Config[]
).map(config => {
  if (config.plugins) {
    const newPlugins = {...config.plugins};
    if (newPlugins['@typescript-eslint'] && primaryTsPlugin) {
      newPlugins['@typescript-eslint'] = primaryTsPlugin;
    }
    if (newPlugins['import'] && primaryImportPlugin) {
      newPlugins['import'] = primaryImportPlugin;
    }
    return {...config, plugins: newPlugins};
  }
  return config;
});

export default combined;
