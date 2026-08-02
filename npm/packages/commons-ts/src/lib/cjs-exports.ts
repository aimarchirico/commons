import type {Rule} from 'eslint';

type DeclarationNode = Rule.Node;

/**
 * Whether an expression roots at `module.exports` or `exports`, covering
 * `module.exports = ...`, `module.exports.foo = ...`, and `exports.foo = ...`.
 * @param node The expression to check, typically an assignment's `left`.
 * @returns Whether the expression is a CommonJS export target.
 */
export function isCommonJSExportTarget(node: DeclarationNode): boolean {
  if (node.type === 'Identifier') return node.name === 'exports';
  if (node.type !== 'MemberExpression') return false;
  const isModuleExports =
    !node.computed &&
    node.object.type === 'Identifier' &&
    node.object.name === 'module' &&
    node.property.type === 'Identifier' &&
    node.property.name === 'exports';
  return (
    isModuleExports || isCommonJSExportTarget(node.object as DeclarationNode)
  );
}
