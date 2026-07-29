import type {ESLint} from 'eslint';
import {noNonJSDocComment} from './comments';

/** Plugin namespace holding the custom lint rules shared with consumers. */
export const commonsPlugin: ESLint.Plugin = {
  rules: {'no-non-jsdoc-comment': noNonJSDocComment},
};
