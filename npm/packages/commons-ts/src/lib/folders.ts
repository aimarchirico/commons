/** Folder names allowed directly under `src` by default. */
export const CORE_FOLDERS = [
  'assets',
  'bin',
  'lib',
  'services',
  'types',
  'utils',
];

/**
 * Joins folder names into an alternation the naming convention rule accepts.
 *
 * @param folders The folder names allowed directly under `src`.
 * @returns The alternation group, e.g. `(bin|lib)`.
 */
export const buildRegex = (folders: string[]) => `(${folders.join('|')})`;

/**
 * Builds the config block restricting which folders may sit under `src`.
 *
 * @param folders The folder names to allow. Defaults to {@link CORE_FOLDERS}.
 * @returns A flat config block for the folder naming convention.
 */
export const folderRule = (folders: string[] = CORE_FOLDERS) => ({
  files: ['**/src/**/*'],
  rules: {
    'check-file/folder-naming-convention': [
      'error',
      {
        '**/src/*/': buildRegex(folders),
      },
    ],
  },
});
