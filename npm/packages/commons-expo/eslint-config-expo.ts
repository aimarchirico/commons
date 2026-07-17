import type {Linter} from 'eslint';
// @ts-expect-error eslint-config-expo ships no type declarations
import config from 'eslint-config-expo/flat.js';

export const expoConfig = config as Linter.Config[];
