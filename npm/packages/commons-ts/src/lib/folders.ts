export const CORE_FOLDERS = [
  'bin',
  'lib',
  'locales',
  'services',
  'types',
  'utils',
];

export const buildRegex = (folders: string[]) => `(${folders.join('|')})`;

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
