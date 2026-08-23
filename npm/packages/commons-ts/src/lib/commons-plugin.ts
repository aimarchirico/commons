import type {ESLint} from 'eslint';
import {defaultExportShape} from './default-export-shape';

/** Plugin namespace holding the custom lint rules shared with consumers. */
export const commonsPlugin: ESLint.Plugin = {
  rules: {
    'default-export-shape': defaultExportShape,
  },
};
