import {CORE_FOLDERS as TS_FOLDERS} from '@aimarchirico/commons-ts/folders';

/** Folder names allowed directly under `src`, extending the shared TS set. */
export const CORE_FOLDERS = [...TS_FOLDERS, 'contexts', 'hooks', 'locales'];

/** {@link CORE_FOLDERS} plus the folders that hold UI code. */
export const UI_FOLDERS = [...CORE_FOLDERS, 'components', 'screens', 'styles'];

/** Folder names allowed directly under the app root. */
export const APP_FOLDERS = ['app', 'assets', 'lib'];
