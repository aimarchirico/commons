export const FOLDERS = [
  'lib',
  'core',
  'services',
  'utils',
  'config',
  'models',
  'types',
  'api',
  'hooks',
  'components',
  'constants',
  'store'
];

export const buildRegex = (folders: string[]) => `^(${folders.join('|')})$`;
