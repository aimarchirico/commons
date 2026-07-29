import type {Rule, SourceCode} from 'eslint';

type Comment = ReturnType<SourceCode['getAllComments']>[number];

/**
 * Comment prefixes that tooling reads as instructions rather than as prose.
 *
 * Compilers and formatters only recognise these in their plain form, so they
 * cannot be rewritten as documentation blocks. Banning them outright would
 * leave no way to write a suppression.
 */
export const DIRECTIVE_PREFIXES = [
  'eslint',
  'exported',
  'global',
  'globals',
  'prettier-ignore',
  'ts-check',
  'ts-expect-error',
  'ts-ignore',
  'ts-nocheck',
  'typescript-eslint',
];

const directivePattern = new RegExp(
  `^\\s*@?(${DIRECTIVE_PREFIXES.join('|')})\\b`,
);

/**
 * Reports whether a comment is a JSDoc block, which stays legal.
 *
 * @param comment - The comment to test.
 * @returns Whether the comment is a JSDoc block.
 */
const isJSDoc = (comment: Comment): boolean =>
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
 * Bans every comment except JSDoc blocks and tooling directives.
 *
 * Explanation belongs in a JSDoc block attached to the construct it
 * describes. A line comment or a plain block comment is therefore always a
 * violation, whether it sits on its own line or trails code.
 */
export const noNonJSDocComment: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Allow only JSDoc blocks and tooling directives.',
    },
    schema: [],
    messages: {
      nonJSDocComment:
        'Only JSDoc blocks are allowed. Attach the explanation to the construct it describes, or delete it.',
    },
  },
  create: context => ({
    Program: () => {
      for (const comment of context.sourceCode.getAllComments()) {
        /**
         * ESLint tags a `//` comment `Line` and a `/* *\/` comment `Block`;
         * both count as plain comments here.
         */
        const isPlain = comment.type === 'Line' || comment.type === 'Block';
        if (!isPlain || isJSDoc(comment) || isDirective(comment)) {
          continue;
        }
        const {loc} = comment;
        if (loc) {
          context.report({loc, messageId: 'nonJSDocComment'});
        }
      }
    },
  }),
};
