export const FOLDERS = ['assets', 'bin', 'lib', 'services', 'types', 'utils'];

export const buildRegex = (folders: string[]) => `(${folders.join('|')})`;

export const folderRule = (folders: string[] = FOLDERS) => ({
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
