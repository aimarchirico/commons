import type {ESLint} from 'eslint';
import {publicJSDocOnly} from './comments';
import {defaultExportShape} from './default-export-shape';

/** Plugin namespace holding the custom lint rules shared with consumers. */
export const commonsPlugin: ESLint.Plugin = {
  rules: {
    'public-jsdoc-only': publicJSDocOnly,
    'default-export-shape': defaultExportShape,
  },
};
