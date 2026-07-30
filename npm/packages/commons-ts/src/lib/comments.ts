import {getJSDocComment} from '@es-joy/jsdoccomment';
import type {Rule, SourceCode} from 'eslint';

type Comment = ReturnType<SourceCode['getAllComments']>[number];
type DeclarationNode = Rule.Node;

/**
 * Node types eligible to carry a JSDoc block. This mirrors the broad set that
 * `jsdoc/require-jsdoc`'s `require`/`contexts` options target in
 * `eslint-base.ts`: exported top-level functions, classes, interfaces, type
 * aliases, enums, and exported `const`/`let`/`var` declarations, plus public
 * members of exported classes. The require-side and prohibit-side rules must
 * agree on exactly this set.
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
] as const;

/**
 * Node types `jsdoc/require-jsdoc`'s `require` option supports directly. Any
 * `DOC_ELIGIBLE_VISITORS` entry outside this set is passed through
 * `contexts` instead, so the require-side rule targets exactly the same
 * declarations that `commons/public-jsdoc-only` allows to carry a JSDoc
 * block.
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

/** Class member node types whose exported-ness follows their enclosing class. */
const CLASS_MEMBER_TYPES = new Set<string>([
  'MethodDefinition',
  'PropertyDefinition',
  'TSAbstractMethodDefinition',
  'TSAbstractPropertyDefinition',
]);

/** Settings passed to `getJSDocComment`; only `minLines`/`maxLines` are read. */
const JSDOC_COMMENT_SETTINGS = {maxLines: 1, minLines: 0};

/**
 * Comment prefixes that tooling reads as instructions rather than as prose.
 *
 * Compilers only recognise these in their plain form, so they cannot be
 * rewritten as documentation blocks. Banning them outright would leave no
 * way to write a suppression.
 *
 * The four `eslint-disable*`/`eslint-enable` forms are exactly what
 * `@eslint-community/eslint-comments`'s `no-unlimited-disable`,
 * `no-unused-disable`, and `require-description` rules (configured in
 * `eslint-base.ts`) govern: those rules require the comments to name specific
 * rule(s) and include a `-- description`, but the comments themselves remain
 * legitimate, so they must stay recognised as directives here.
 *
 * `ts-ignore` and `ts-nocheck` are deliberately absent: `ban-ts-comment`
 * hard-bans both, so treating them as a recognised directive here would let a
 * banned-but-still-typed `@ts-ignore` slip past this rule while still being
 * flagged by `ban-ts-comment`. `ts-expect-error` stays, since it remains a
 * legal comment shape (requiring a description) independent of that rule.
 */
export const DIRECTIVE_PREFIXES = [
  'eslint-disable',
  'eslint-disable-line',
  'eslint-disable-next-line',
  'eslint-enable',
  'exported',
  'global',
  'globals',
  'ts-check',
  'ts-expect-error',
  'x-release-please-version',
];

const directivePattern = new RegExp(
  `^\\s*@?(${DIRECTIVE_PREFIXES.join('|')})\\b`,
);

/**
 * Reports whether a comment is shaped like a JSDoc block.
 *
 * @param comment - The comment to test.
 * @returns Whether the comment has the JSDoc `/**` shape.
 */
const isJSDocShaped = (comment: Comment): boolean =>
  comment.type === 'Block' && comment.value.startsWith('*');

/**
 * Reports whether a comment carries an instruction for another tool.
 *
 * @param comment - The comment to test.
 * @returns Whether the comment is a tooling directive.
 */
const isDirective = (comment: Comment): boolean =>
  directivePattern.test(comment.value);

/**
 * Reports whether a class member is inaccessible from outside its class,
 * either through a `private`/`protected` TypeScript modifier or a `#private`
 * JavaScript field/method name.
 *
 * @param node - The class member node to test.
 * @returns Whether the member is non-public.
 */
const isNonPublicMember = (node: DeclarationNode): boolean => {
  const accessibility =
    'accessibility' in node
      ? (node as {accessibility?: string}).accessibility
      : undefined;
  if (accessibility === 'private' || accessibility === 'protected') {
    return true;
  }
  const key =
    'key' in node ? (node as {key?: {type?: string}}).key : undefined;
  return key?.type === 'PrivateIdentifier';
};

/**
 * Reports whether a declaration is directly exported, following `const`
 * bindings up to their `export` statement, and class members up to their
 * enclosing class.
 *
 * @param node - The declaration node to test.
 * @returns Whether the declaration is exported (or, for a class member,
 *   public and belonging to an exported class).
 */
const isExported = (node: DeclarationNode): boolean => {
  let current: DeclarationNode = node;

  if (CLASS_MEMBER_TYPES.has(current.type)) {
    if (isNonPublicMember(current)) {
      return false;
    }
    const classBody = current.parent;
    if (!classBody || classBody.type !== 'ClassBody' || !classBody.parent) {
      return false;
    }
    current = classBody.parent;
  }

  while (current.parent) {
    const {parent} = current;
    if (
      parent.type === 'ExportNamedDeclaration' ||
      parent.type === 'ExportDefaultDeclaration'
    ) {
      return true;
    }
    if (
      parent.type === 'VariableDeclarator' ||
      parent.type === 'VariableDeclaration'
    ) {
      current = parent;
      continue;
    }
    return false;
  }
  return false;
};

/**
 * Records the JSDoc comment owned by a doc-eligible declaration node, if any.
 *
 * @param sourceCode - The source under lint.
 * @param owners - The map being built from comment to owning declaration.
 * @param node - The declaration node to resolve a JSDoc comment for.
 */
const recordOwner = (
  sourceCode: SourceCode,
  owners: Map<Comment, DeclarationNode>,
  node: DeclarationNode,
): void => {
  const comment = getJSDocComment(sourceCode, node, JSDOC_COMMENT_SETTINGS);
  if (comment) {
    owners.set(comment as Comment, node);
  }
};

/**
 * Bans every comment except JSDoc blocks that document a public (exported)
 * declaration, plus tooling directives.
 *
 * Explanation belongs in a JSDoc block attached to the exported construct it
 * describes. A line comment, a plain block comment, an orphaned JSDoc block
 * with no owning declaration, or a JSDoc block on a non-exported declaration
 * is therefore always a violation.
 */
export const publicJSDocOnly: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Allow only JSDoc blocks documenting public (exported) declarations, and tooling directives.',
    },
    schema: [],
    messages: {
      nonJSDocComment:
        'Only JSDoc blocks are allowed. Attach the explanation to the construct it describes, or delete it.',
      orphanedJSDoc:
        'This JSDoc block does not document any declaration. Attach it to one, or delete it.',
      nonPublicJSDoc:
        'JSDoc blocks are reserved for exported declarations. Export the declaration, or delete this comment.',
    },
  },
  create: context => {
    const {sourceCode} = context;
    const owners = new Map<Comment, DeclarationNode>();
    const trackOwner = (node: DeclarationNode): void =>
      recordOwner(sourceCode, owners, node);

    const visitors: Rule.RuleListener = Object.fromEntries(
      DOC_ELIGIBLE_VISITORS.map(type => [type, trackOwner]),
    );

    return {
      ...visitors,
      'Program:exit': () => {
        for (const comment of sourceCode.getAllComments()) {
          /**
           * ESLint tags a `//` comment `Line` and a `/* *\/` comment `Block`;
           * both count as plain comments here.
           */
          const isPlain = comment.type === 'Line' || comment.type === 'Block';
          if (!isPlain || isDirective(comment)) {
            continue;
          }
          const {loc} = comment;
          if (!loc) {
            continue;
          }
          if (!isJSDocShaped(comment)) {
            context.report({loc, messageId: 'nonJSDocComment'});
            continue;
          }
          const owner = owners.get(comment);
          if (!owner) {
            context.report({loc, messageId: 'orphanedJSDoc'});
            continue;
          }
          if (!isExported(owner)) {
            context.report({loc, messageId: 'nonPublicJSDoc'});
          }
        }
      },
    };
  },
};
