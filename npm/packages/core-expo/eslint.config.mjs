import {defineConfig} from 'eslint/config';
import expoConfig from 'eslint-config-expo/flat.js';
import coreConfig from '@aimarchirico/core-ts/eslint';

export default defineConfig([...expoConfig, ...coreConfig]);
