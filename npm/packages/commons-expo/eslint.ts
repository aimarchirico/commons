import expoConfig from 'eslint-config-expo/flat.js';
import baseConfig from '@aimarchirico/commons-ts/eslint';

const flatExpo = expoConfig.flat(Infinity);
const primaryTsPlugin = flatExpo.find(
  c => c && c.plugins && c.plugins['@typescript-eslint'],
)?.plugins['@typescript-eslint'];
const primaryImportPlugin = flatExpo.find(
  c => c && c.plugins && c.plugins['import'],
)?.plugins['import'];

const combined = [...expoConfig, ...baseConfig].flat(Infinity).map(config => {
  if (config && config.plugins) {
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
