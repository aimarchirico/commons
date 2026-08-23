/**
 * Node types eligible to carry a JSDoc block. This mirrors the broad set that
 * `jsdoc/require-jsdoc`'s `require`/`contexts` options target in
 * `eslint-base.ts`: exported top-level functions, classes, interfaces, type
 * aliases, enums, and exported `const`/`let`/`var` declarations, plus public
 * members of exported classes.
 */
export const DOC_ELIGIBLE_VISITORS = [
  'ArrowFunctionExpression',
  'ClassDeclaration',
  'ClassExpression',
  'FunctionDeclaration',
  'FunctionExpression',
  'TSInterfaceDeclaration',
  'TSTypeAliasDeclaration',
  'TSEnumDeclaration',
  'VariableDeclarator',
  'MethodDefinition',
  'PropertyDefinition',
  'TSAbstractMethodDefinition',
  'TSAbstractPropertyDefinition',
  'ExportDefaultDeclaration > CallExpression',
  'ExportDefaultDeclaration > ObjectExpression',
] as const;

/**
 * Node types `jsdoc/require-jsdoc`'s `require` option supports directly. Any
 * `DOC_ELIGIBLE_VISITORS` entry outside this set is passed through
 * `contexts` instead.
 */
export const JSDOC_REQUIRE_KEYS = new Set([
  'ArrowFunctionExpression',
  'ClassDeclaration',
  'ClassExpression',
  'FunctionDeclaration',
  'FunctionExpression',
  'MethodDefinition',
]);

/** `jsdoc/require-jsdoc`'s `require` option, derived from `DOC_ELIGIBLE_VISITORS`. */
export const jsdocRequire = Object.fromEntries(
  DOC_ELIGIBLE_VISITORS.filter(type => JSDOC_REQUIRE_KEYS.has(type)).map(
    type => [type, true],
  ),
);

/** `jsdoc/require-jsdoc`'s `contexts` option, derived from `DOC_ELIGIBLE_VISITORS`. */
export const jsdocContexts = DOC_ELIGIBLE_VISITORS.filter(
  type => !JSDOC_REQUIRE_KEYS.has(type),
);
