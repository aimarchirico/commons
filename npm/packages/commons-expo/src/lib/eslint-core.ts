import type {Linter} from 'eslint';
import baseConfig from '@aimarchirico/commons-ts/eslint-base';
import {folderRule} from '@aimarchirico/commons-ts/folders';
import {expoConfig} from './eslint-config-expo';
import {CORE_FOLDERS} from './folders';

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

export default [
  ...combined,
  folderRule(CORE_FOLDERS),
  {
    files: ['**/*.{web,android}.ts'],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },
];
