import type {ESLint, Rule, SourceCode} from 'eslint';

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

/** Reports whether a comment is a documentation block, which stays legal. */
const isDocBlock = (comment: Comment): boolean =>
  comment.type === 'Block' && comment.value.startsWith('*');

/** Reports whether a comment carries an instruction for another tool. */
const isDirective = (comment: Comment): boolean =>
  directivePattern.test(comment.value);

/**
 * Bans every comment except documentation blocks and tooling directives.
 *
 * Explanation belongs in a documentation block attached to the construct it
 * describes. A line comment or a plain block comment is therefore always a
 * violation, whether it sits on its own line or trails code.
 */
export const noNonDocComment: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Allow only documentation blocks and tooling directives.',
    },
    schema: [],
    messages: {
      nonDocComment:
        'Only documentation blocks are allowed. Attach the explanation to the construct it describes, or delete it.',
    },
  },
  create: context => ({
    Program: () => {
      for (const comment of context.sourceCode.getAllComments()) {
        const isPlain = comment.type === 'Line' || comment.type === 'Block';
        if (!isPlain || isDocBlock(comment) || isDirective(comment)) {
          continue;
        }
        const {loc} = comment;
        if (loc) {
          context.report({loc, messageId: 'nonDocComment'});
        }
      }
    },
  }),
};

/** Plugin namespace holding the documentation rules shared with consumers. */
export const commonsPlugin: ESLint.Plugin = {
  rules: {'no-non-doc-comment': noNonDocComment},
};
