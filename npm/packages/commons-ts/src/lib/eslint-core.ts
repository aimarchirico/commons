import {defineConfig} from 'eslint/config';
import baseConfig from './eslint-base';
import {folderRule} from './folders';

/** Shared ESLint core configuration. */
export default defineConfig([...baseConfig, folderRule()]);
