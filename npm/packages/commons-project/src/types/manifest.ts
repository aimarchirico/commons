/** A single renaming value, as its source (`from`) and target (`to`) form. */
export type ManifestValue = {from: string; to: string};

/** A rule replacing occurrences of a manifest value's text across files. */
export type ManifestReplacement = {
  value: string;
  transforms?: string[];
  files: string[];
};

/** An instruction to move (or rename) a file or directory. */
export type ManifestMove = {from: string; to: string};

/** The full set of instructions describing a project rename. */
export type Manifest = {
  values: Record<string, ManifestValue>;
  replacements?: ManifestReplacement[];
  moves?: ManifestMove[];
  deletes?: string[];
};
