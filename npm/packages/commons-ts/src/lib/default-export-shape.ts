import type {Rule} from 'eslint';

const ALLOWED_DECLARATION_TYPES = new Set([
  'Identifier',
  'FunctionDeclaration',
  'ClassDeclaration',
]);

/**
 * Restricts `export default` to an identifier referencing a documented
 * `const`, or a named function/class declaration.
 *
 * `*.config.ts` is the only place `import/no-default-export` is relaxed
 * (`eslint-base.ts`), so this rule targets the same files. Without it, the
 * default-export value can be an inline object/array/call expression that
 * `commons/public-jsdoc-only` has no attachment point for, so a JSDoc block
 * placed above it is always reported as orphaned. Forcing the value behind a
 * named `const` gives it somewhere to carry a doc block; function/class
 * declarations already have one because their parent can be the
 * `ExportDefaultDeclaration` node directly.
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
