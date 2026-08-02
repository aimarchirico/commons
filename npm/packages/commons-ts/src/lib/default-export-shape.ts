import type {Rule} from 'eslint';

const ALLOWED_EXPORT_SHAPES = new Set([
  'CallExpression',
  'FunctionDeclaration',
  'ClassDeclaration',
  'ObjectExpression',
]);

/**
 * ESLint rule restricting `export default` to a call expression, named
 * function/class declaration, or an object literal.
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
        'Export a named function, class, or a call expression instead of {{type}}.',
    },
  },
  create: context => ({
    ExportDefaultDeclaration: node => {
      const {declaration} = node;
      if (!ALLOWED_EXPORT_SHAPES.has(declaration.type)) {
        context.report({
          node: declaration,
          messageId: 'inlineDefaultExport',
          data: {type: declaration.type},
        });
      }
    },
  }),
};
