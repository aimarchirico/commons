import type {Rule} from 'eslint';

const ALLOWED_DECLARATION_TYPES = new Set([
  'Identifier',
  'FunctionDeclaration',
  'ClassDeclaration',
]);

/**
 * ESLint rule restricting `export default` to an identifier, named function,
 * or class declaration.
 */
export const defaultExportShape: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Restrict export default to a documented identifier or a named function/class declaration.',
    },
    schema: [],
    messages: {
      inlineDefaultExport:
        'Assign this to a documented `const` and export that identifier instead of exporting {{type}} directly.',
    },
  },
  create: context => ({
    ExportDefaultDeclaration: node => {
      const {declaration} = node;
      if (!ALLOWED_DECLARATION_TYPES.has(declaration.type)) {
        context.report({
          node: declaration,
          messageId: 'inlineDefaultExport',
          data: {type: declaration.type},
        });
      }
    },
  }),
};
