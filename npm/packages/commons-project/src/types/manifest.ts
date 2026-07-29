export type ManifestValue = {from: string; to: string};

export type ManifestReplacement = {
  value: string;
  transforms?: string[];
  files: string[];
};

export type ManifestMove = {from: string; to: string};

export type Manifest = {
  values: Record<string, ManifestValue>;
  replacements?: ManifestReplacement[];
  moves?: ManifestMove[];
  deletes?: string[];
};
