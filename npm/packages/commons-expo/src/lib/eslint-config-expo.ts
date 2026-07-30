import type {Linter} from 'eslint';
// @ts-expect-error eslint-config-expo ships no type declarations
import config from 'eslint-config-expo/flat.js';

/** The upstream `eslint-config-expo` flat config, re-typed for ESLint's flat config API. */
export const expoConfig = config as Linter.Config[];
